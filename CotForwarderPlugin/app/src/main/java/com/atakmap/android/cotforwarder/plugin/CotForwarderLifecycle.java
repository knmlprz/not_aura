
package com.atakmap.android.cotforwarder.plugin;

import com.atak.plugins.impl.AbstractPlugin;
import com.atak.plugins.impl.PluginContextProvider;
import com.atakmap.android.cotforwarder.CotForwarderMapComponent;

import gov.tak.api.plugin.IServiceController;

/**
 * Plugin entry point. Declared in {@code assets/plugin.xml} as the
 * {@code gov.tak.api.plugin.IPlugin} implementation, so ATAK instantiates this
 * class (via reflection) when the user loads the plugin from the Plugin Manager.
 *
 * <p>Modeled on the SDK {@code samples/selfmarkerdata}: a thin {@link AbstractPlugin}
 * that wires in a single {@link CotForwarderMapComponent}. This plugin deliberately
 * has no toolbar Tool/button of its own — all of its UI is the radial-menu toggle
 * plus the preference screen, both registered by the MapComponent.
 */
public class CotForwarderLifecycle extends AbstractPlugin {

    public CotForwarderLifecycle(IServiceController serviceController) {
        // AbstractPlugin takes the MapComponent that holds this plugin's lifecycle.
        super(serviceController, new CotForwarderMapComponent());

        // Initialize the native-library loader (standard ATAK boilerplate). This is
        // safe even though we ship no .so files — it simply records the native lib
        // directory so loadLibrary() could be used later if ever needed.
        PluginNativeLoader.init(serviceController
                .getService(PluginContextProvider.class).getPluginContext());
    }
}
