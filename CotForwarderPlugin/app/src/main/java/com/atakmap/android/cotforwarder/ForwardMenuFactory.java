
package com.atakmap.android.cotforwarder;

import android.content.Context;

import com.atakmap.android.maps.MapDataRef;
import com.atakmap.android.maps.MapItem;
import com.atakmap.android.maps.MapView;
import com.atakmap.android.maps.PointMapItem;
import com.atakmap.android.maps.assets.MapAssets;
import com.atakmap.android.menu.MapMenuButtonWidget;
import com.atakmap.android.menu.MapMenuFactory;
import com.atakmap.android.menu.MapMenuWidget;
import com.atakmap.android.menu.MenuMapAdapter;
import com.atakmap.android.menu.MenuResourceFactory;
import com.atakmap.android.menu.PluginMenuParser;
import com.atakmap.android.widgets.MapWidget;
import com.atakmap.android.widgets.WidgetIcon;
import com.atakmap.coremap.log.Log;

import java.io.IOException;

import gov.tak.api.widgets.IMapMenuButtonWidget;

/**
 * Injects an ON/OFF toggle button into the radial menu of "atom" markers
 * (PointMapItem whose type starts with {@code a-}: a-f / a-h / a-n / a-u ...).
 *
 * <p>Pattern from {@code samples/helloworld/menu/MenuFactory.java}: we let
 * {@link MenuResourceFactory} build the DEFAULT radial menu (so all of ATAK's
 * standard buttons are preserved) and then append our own button. The button's
 * icon reflects the current ON/OFF state stored in the marker's metadata.
 *
 * <p>Two non-obvious requirements when adding a button to an existing menu (both
 * learned the hard way — see the comments inline):
 * <ul>
 *   <li>{@code setButtonSize(span, width)} MUST be called, else the button collapses
 *       into the menu center and overlaps the marker (no clickable icon).</li>
 *   <li>The button must be added via {@code addChildWidgetAt(...)}, not
 *       {@code addWidget(...)} — the latter only draws it, it is not wired into the
 *       menu's click dispatch and so taps are ignored.</li>
 * </ul>
 */
public class ForwardMenuFactory implements MapMenuFactory {

    public static final String TAG = "CotFwd.MenuFactory";

    private final Context pluginContext;
    private final ForwardManager manager;
    private final MenuResourceFactory resourceFactory;

    public ForwardMenuFactory(final Context pluginContext,
            final ForwardManager manager) {
        this.pluginContext = pluginContext;
        this.manager = manager;

        final MapView mapView = MapView.getMapView();
        final Context appContext = mapView.getContext();
        // Use the APPLICATION assets (not the plugin's) — hence the app context.
        final MapAssets mapAssets = new MapAssets(appContext);
        final MenuMapAdapter adapter = new MenuMapAdapter();
        try {
            adapter.loadMenuFilters(mapAssets, "filters/menu_filters.xml");
        } catch (IOException e) {
            Log.w(TAG, "nie udalo sie zaladowac menu_filters.xml", e);
        }
        resourceFactory = new MenuResourceFactory(mapView, mapView.getMapData(),
                mapAssets, adapter);
    }

    /**
     * Called by ATAK whenever a marker's radial menu is about to be shown.
     * Return a menu to use, or {@code null} to let ATAK build the default one.
     */
    @Override
    public MapMenuWidget create(MapItem item) {
        // Only act on point markers of an "atom" type (a-*).
        if (!(item instanceof PointMapItem))
            return null;
        final String type = item.getType();
        if (type == null || !type.startsWith("a-"))
            return null;

        // Build the default radial menu for this marker (keeps ATAK's own buttons).
        final MapMenuWidget menu = resourceFactory.create(item);
        if (menu == null)
            return null;

        final boolean on = item.getMetaBoolean(ForwardManager.META_KEY, false);

        // Pattern from samples/helloworld MenuFactory.addedSubmenuButton: average the
        // span and width of the existing buttons so ours occupies an identical arc
        // slice. Without setButtonSize(...) the button collapses into the menu center
        // and overlaps the marker (no clickable icon).
        float span = 0f;
        float width = 0f;
        int count = 0;
        for (MapWidget child : menu.getChildWidgets()) {
            if (child instanceof MapMenuButtonWidget) {
                final MapMenuButtonWidget b = (MapMenuButtonWidget) child;
                span += b.getButtonSpan();
                width += b.getButtonWidth();
                count++;
            }
        }
        if (count > 0) {
            span /= count;
            width /= count;
        } else {
            // Sensible fallback if the menu somehow had no buttons to measure.
            span = 45f;
            width = 64f;
        }

        final MapMenuButtonWidget btn = new MapMenuButtonWidget(
                MapView.getMapView().getContext());
        btn.setIcon(createWidgetIcon(on
                ? "icons/ic_forward_on.png"
                : "icons/ic_forward_off.png"));
        // span doubles as the layout weight for XML-defined menus; width must be set
        // consistently, otherwise the button has no geometry and does not render.
        btn.setLayoutWeight(span);
        btn.setButtonSize(span, width);
        btn.setOnButtonClickHandler(
                new IMapMenuButtonWidget.OnButtonClickHandler() {
                    @Override
                    public boolean isSupported(Object o) {
                        return o instanceof PointMapItem;
                    }

                    @Override
                    public void performAction(Object o) {
                        if (o instanceof PointMapItem) {
                            final PointMapItem p = (PointMapItem) o;
                            manager.toggle(p);
                            // The radial menu stays open after a tap, so refresh the
                            // icon right away to reflect the new ON/OFF state.
                            final boolean nowOn = p.getMetaBoolean(
                                    ForwardManager.META_KEY, false);
                            btn.setIcon(createWidgetIcon(nowOn
                                    ? "icons/ic_forward_on.png"
                                    : "icons/ic_forward_off.png"));
                        }
                    }
                });

        // Add via addChildWidgetAt (as the sample does when extending an existing
        // menu). addWidget only draws the button — it does NOT wire it into the
        // menu's click dispatch, so taps would be silently ignored.
        menu.addChildWidgetAt(menu.getChildWidgetCount(), btn);
        return menu;
    }

    /**
     * Build a {@link WidgetIcon} from a plugin asset path ({@code assets/icons/...}).
     * {@link PluginMenuParser#getItem} returns an encoded asset URI scoped to the
     * current plugin context; we fall back to a plain asset URI if it returns empty.
     */
    private WidgetIcon createWidgetIcon(String path) {
        String asset = PluginMenuParser.getItem(pluginContext, path);
        if (asset == null || asset.length() == 0) {
            asset = "asset:///" + path;
        }
        final MapDataRef ref = MapDataRef.parseUri(asset);
        final WidgetIcon.Builder builder = new WidgetIcon.Builder();
        return builder
                .setImageRef(0, ref)
                .setAnchor(16, 16)
                .setSize(32, 32)
                .build();
    }
}
