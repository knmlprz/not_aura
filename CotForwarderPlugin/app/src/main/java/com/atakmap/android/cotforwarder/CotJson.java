
package com.atakmap.android.cotforwarder;

import com.atakmap.android.maps.PointMapItem;
import com.atakmap.coremap.log.Log;
import com.atakmap.coremap.maps.coords.GeoPoint;

import org.json.JSONObject;

/**
 * Builds the JSON payloads sent to the Raspberry Pi receiver.
 *
 * <p>This is intentionally a plain JSON shape (not raw CoT XML) so the receiver can
 * be a few lines of any language. Two message types:
 * <pre>
 *   UPDATE: {"action":"UPDATE","uid":..,"type":..,"callsign":..,"lat":..,"lon":..,"hae":..,"time":..}
 *   DELETE: {"action":"DELETE","uid":..,"time":..}
 * </pre>
 * The wire framing (a trailing '\n' per message) is added by {@link NetworkManager},
 * not here — this class only produces the JSON string.
 */
public final class CotJson {

    public static final String TAG = "CotFwd.Json";
    public static final String ACTION_UPDATE = "UPDATE";
    public static final String ACTION_DELETE = "DELETE";

    private CotJson() {
    }

    /**
     * Build an UPDATE payload describing the current position/identity of a marker.
     * Returns {@code null} if the item is null or JSON assembly fails (logged).
     */
    public static String update(PointMapItem item) {
        if (item == null)
            return null;
        try {
            JSONObject o = new JSONObject();
            o.put("action", ACTION_UPDATE);
            o.put("uid", item.getUID());
            o.put("type", item.getType());
            // Fall back to the UID if the marker has no callsign metadata.
            o.put("callsign", item.getMetaString("callsign", item.getUID()));

            GeoPoint p = item.getPoint();
            if (p != null) {
                o.put("lat", p.getLatitude());
                o.put("lon", p.getLongitude());
                // Height above ellipsoid; send 0.0 rather than NaN when unknown.
                double hae = p.getAltitude();
                o.put("hae", Double.isNaN(hae) ? 0.0 : hae);
            }
            o.put("time", System.currentTimeMillis());
            return o.toString();
        } catch (Exception e) {
            Log.e(TAG, "blad budowy JSON UPDATE", e);
            return null;
        }
    }

    /**
     * Build a DELETE payload for a UID (sent on toggle-OFF or marker removal).
     * Returns {@code null} if uid is null or JSON assembly fails (logged).
     */
    public static String delete(String uid) {
        if (uid == null)
            return null;
        try {
            JSONObject o = new JSONObject();
            o.put("action", ACTION_DELETE);
            o.put("uid", uid);
            o.put("time", System.currentTimeMillis());
            return o.toString();
        } catch (Exception e) {
            Log.e(TAG, "blad budowy JSON DELETE", e);
            return null;
        }
    }
}
