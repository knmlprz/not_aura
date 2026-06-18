
package com.atakmap.android.cotforwarder;

import android.annotation.SuppressLint;
import android.content.Context;
import android.os.Bundle;

import com.atakmap.android.cotforwarder.plugin.R;
import com.atakmap.android.preference.PluginPreferenceFragment;

/**
 * The plugin's preference screen (destination IP / port / protocol).
 *
 * <p>Registered with ATAK via {@code ToolsPreferenceFragment} in
 * {@link CotForwarderMapComponent}. The actual values are stored in ATAK's shared
 * preferences (keys {@code cotfwd_ip}, {@code cotfwd_port}, {@code cotfwd_proto},
 * defined in {@code res/xml/preferences.xml}); {@link NetworkManager} reads them and
 * listens for changes so edits take effect without restarting ATAK.
 */
public class CotForwarderPreferenceFragment extends PluginPreferenceFragment {

    public static final String TAG = "CotFwd.Prefs";

    // The plugin context, stashed statically so the no-arg constructor (which the
    // fragment framework may call) can still reach it. See the constructor note below.
    private static Context staticPluginContext;

    /**
     * Fragments require a public no-arg constructor. It is only ever invoked AFTER
     * the 1-arg constructor below has run and populated {@link #staticPluginContext}.
     */
    public CotForwarderPreferenceFragment() {
        super(staticPluginContext, R.xml.preferences);
    }

    @SuppressLint("ValidFragment")
    public CotForwarderPreferenceFragment(final Context pluginContext) {
        super(pluginContext, R.xml.preferences);
        staticPluginContext = pluginContext;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // No extra logic — the preferences are purely declarative in
        // res/xml/preferences.xml; NetworkManager handles reacting to changes.
    }

    @Override
    public String getSubTitle() {
        return getSubTitle("Tool Preferences", "CoT Forwarder");
    }
}
