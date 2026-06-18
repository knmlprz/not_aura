
package com.atakmap.android.cotforwarder;

import android.content.Context;
import android.widget.Toast;

import com.atakmap.android.maps.MapEvent;
import com.atakmap.android.maps.MapEventDispatcher;
import com.atakmap.android.maps.MapGroup;
import com.atakmap.android.maps.MapItem;
import com.atakmap.android.maps.MapView;
import com.atakmap.android.maps.PointMapItem;
import com.atakmap.coremap.log.Log;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Core logic. Owns the per-marker ON/OFF state and the three things that trigger
 * a network message:
 * <ol>
 *   <li>Toggle ON  -> immediate UPDATE, and attach a movement listener.</li>
 *   <li>Marker moves while ON -> another UPDATE (via the movement listener).</li>
 *   <li>Toggle OFF, or the marker is removed from the map -> DELETE.</li>
 * </ol>
 *
 * <p>The ON/OFF state lives in the marker's own metadata ({@link #META_KEY}), so it
 * survives UI refreshes and an ATAK restart (ATAK's statesaver persists metadata).
 * On (re)start {@link #reattachExistingEnabledItems()} re-arms movement listeners
 * for markers that were left ON.
 */
public class ForwardManager
        implements MapEventDispatcher.MapEventDispatchListener {

    public static final String TAG = "CotFwd.Manager";

    /** Metadata key holding the ON/OFF state. Persisted by ATAK's statesaver. */
    public static final String META_KEY = "cotfwd.enabled";

    private final MapView mapView;
    private final NetworkManager net;

    // UID -> movement listener, kept so we can detach it later.
    private final Map<String, PointMapItem.OnPointChangedListener> listeners =
            new ConcurrentHashMap<>();

    public ForwardManager(MapView mapView, NetworkManager net) {
        this.mapView = mapView;
        this.net = net;
    }

    public void start() {
        // Listen globally for markers being removed from the map.
        mapView.getMapEventDispatcher()
                .addMapEventListener(MapEvent.ITEM_REMOVED, this);
        // After a (re)start, re-arm movement listeners for markers still flagged ON.
        reattachExistingEnabledItems();
    }

    /** Flip ON/OFF for a marker — invoked from the radial-menu button. */
    public void toggle(PointMapItem item) {
        if (item == null)
            return;
        boolean now = !item.getMetaBoolean(META_KEY, false);
        item.setMetaBoolean(META_KEY, now); // persist the new state in metadata
        if (now)
            enable(item);
        else
            disable(item);
    }

    private void enable(PointMapItem item) {
        attachPointListener(item);
        net.send(CotJson.update(item)); // send an UPDATE immediately on enable
        toast("Przesylanie WL: " + callsign(item));
        Log.d(TAG, "ON " + item.getUID());
    }

    private void disable(PointMapItem item) {
        detachPointListener(item);
        net.send(CotJson.delete(item.getUID())); // send a DELETE on disable
        toast("Przesylanie WYL: " + callsign(item));
        Log.d(TAG, "OFF " + item.getUID());
    }

    private String callsign(PointMapItem item) {
        return item.getMetaString("callsign", item.getUID());
    }

    /** Short on-screen message — immediate, unambiguous feedback for a toggle. */
    private void toast(final String msg) {
        final Context ctx = mapView.getContext();
        mapView.post(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(ctx, msg, Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void attachPointListener(final PointMapItem item) {
        if (listeners.containsKey(item.getUID()))
            return;
        // Anonymous class rather than a lambda — the SDK README warns that lambdas can
        // be broken by proguard in release builds.
        PointMapItem.OnPointChangedListener l =
                new PointMapItem.OnPointChangedListener() {
                    @Override
                    public void onPointChanged(PointMapItem changed) {
                        net.send(CotJson.update(changed)); // movement -> fresh UPDATE
                    }
                };
        item.addOnPointChangedListener(l);
        listeners.put(item.getUID(), l);
    }

    private void detachPointListener(PointMapItem item) {
        PointMapItem.OnPointChangedListener l = listeners.remove(item.getUID());
        if (l != null)
            item.removeOnPointChangedListener(l);
    }

    /** Global ITEM_REMOVED callback: a marker that was ON got deleted -> send DELETE. */
    @Override
    public void onMapEvent(MapEvent event) {
        if (event == null)
            return;
        MapItem mi = event.getItem();
        if (!(mi instanceof PointMapItem))
            return;
        if (mi.getMetaBoolean(META_KEY, false)) {
            detachPointListener((PointMapItem) mi);
            net.send(CotJson.delete(mi.getUID())); // removed ON marker -> DELETE
            Log.d(TAG, "USUNIETO -> DELETE " + mi.getUID());
        }
    }

    /**
     * After an ATAK/plugin restart, markers that were ON still carry META_KEY=true
     * (kept by the statesaver). Walk the map and re-arm their movement listeners.
     */
    private void reattachExistingEnabledItems() {
        try {
            mapView.getRootGroup().deepForEachItem(
                    new MapGroup.MapItemsCallback() {
                        @Override
                        public boolean onItemFunction(MapItem item) {
                            if (item instanceof PointMapItem
                                    && item.getMetaBoolean(META_KEY, false)) {
                                attachPointListener((PointMapItem) item);
                                Log.d(TAG, "re-aktywacja ON " + item.getUID());
                            }
                            return false; // false = keep iterating
                        }
                    });
        } catch (Exception e) {
            Log.e(TAG, "blad re-aktywacji znacznikow ON", e);
        }
    }

    /** Cleanup, invoked from onDestroyImpl. Detaches every listener. */
    public void dispose() {
        mapView.getMapEventDispatcher()
                .removeMapEventListener(MapEvent.ITEM_REMOVED, this);
        for (Map.Entry<String, PointMapItem.OnPointChangedListener> e
                : listeners.entrySet()) {
            MapItem mi = mapView.getMapItem(e.getKey());
            if (mi instanceof PointMapItem)
                ((PointMapItem) mi).removeOnPointChangedListener(e.getValue());
        }
        listeners.clear();
    }
}
