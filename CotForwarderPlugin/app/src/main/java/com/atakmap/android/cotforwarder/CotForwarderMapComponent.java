
package com.atakmap.android.cotforwarder;

import android.content.Context;
import android.content.Intent;

import com.atakmap.android.cotforwarder.plugin.R;
import com.atakmap.android.dropdown.DropDownMapComponent;
import com.atakmap.android.maps.MapView;
import com.atakmap.android.menu.MapMenuReceiver;
import com.atakmap.app.preferences.ToolsPreferenceFragment;
import com.atakmap.coremap.log.Log;

/**
 * The plugin's main MapComponent — the central wiring point and lifecycle owner.
 *
 * <p>ATAK calls {@link #onCreate} when the plugin is loaded and {@link #onDestroyImpl}
 * when it is unloaded (or ATAK shuts down). onCreate builds the three collaborators
 * and registers the radial-menu factory and the preference screen; onDestroyImpl
 * tears everything down in reverse order so no listeners or sockets leak.
 *
 * <p>Collaborators:
 * <ul>
 *   <li>{@link NetworkManager} — all socket I/O on a background executor.</li>
 *   <li>{@link ForwardManager} — per-marker ON/OFF state + movement/removal listeners.</li>
 *   <li>{@link ForwardMenuFactory} — injects the ON/OFF button into the radial menu.</li>
 * </ul>
 */
public class CotForwarderMapComponent extends DropDownMapComponent {

    public static final String TAG = "CotForwarderMapComponent";

    /** Key under which our entry is registered in ATAK's Tool Preferences list. */
    private static final String PREF_KEY = "cotForwarderPreference";

    private Context pluginContext;
    private NetworkManager networkManager;
    private ForwardManager forwardManager;
    private ForwardMenuFactory menuFactory;

    @Override
    public void onCreate(Context context, Intent intent, MapView view) {
        // Apply the plugin theme. The AndroidManifest theme is NOT used in plugin
        // context, so the theme must be set explicitly here before super.onCreate.
        context.setTheme(R.style.ATAKPluginTheme);
        super.onCreate(context, intent, view);
        this.pluginContext = context;

        // 1) Network manager: single-threaded executor + reacts to preference changes.
        networkManager = new NetworkManager(context);

        // 2) Core logic: marker ON/OFF state + movement/removal listeners.
        forwardManager = new ForwardManager(view, networkManager);
        forwardManager.start();

        // 3) Inject the ON/OFF toggle button into the marker radial menu.
        menuFactory = new ForwardMenuFactory(pluginContext, forwardManager);
        MapMenuReceiver.getInstance().registerMapMenuFactory(menuFactory);

        // 4) Register the preference screen (IP / port / protocol) under Tool Preferences.
        ToolsPreferenceFragment.register(
                new ToolsPreferenceFragment.ToolPreference(
                        pluginContext.getString(R.string.app_name),
                        pluginContext.getString(R.string.app_desc),
                        PREF_KEY,
                        pluginContext.getResources().getDrawable(
                                R.drawable.ic_launcher, null),
                        new CotForwarderPreferenceFragment(pluginContext)));

        Log.d(TAG, "CoT Forwarder uruchomiony");
    }

    @Override
    protected void onDestroyImpl(Context context, MapView view) {
        // Tear down in reverse order — safely detach every listener and close sockets.
        if (menuFactory != null)
            MapMenuReceiver.getInstance().unregisterMapMenuFactory(menuFactory);
        ToolsPreferenceFragment.unregister(PREF_KEY);
        if (forwardManager != null)
            forwardManager.dispose();
        if (networkManager != null)
            networkManager.dispose();
        Log.d(TAG, "CoT Forwarder zatrzymany");
        super.onDestroyImpl(context, view);
    }
}
