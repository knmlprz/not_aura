
package com.atakmap.android.cotforwarder.plugin;

import java.io.File;
import android.content.Context;

/**
 * Boilerplate for loading native libraries from within a plugin.
 *
 * <p>Copied verbatim from the ATAK plugin template. It MUST live in this plugin's
 * own unique package (not shared with ATAK core), otherwise class-loader scoping
 * breaks. This plugin currently ships no native (.so) libraries, so the loader is
 * never actually used — it is kept only to match the template and to make adding
 * native code later a one-liner ({@link #loadLibrary(String)}).
 */
public class PluginNativeLoader {

    private static final String TAG = "NativeLoader";

    /** Absolute path to this plugin's native library directory (resolved once). */
    private static String ndl = null;

    /**
     * Resolve and cache the plugin's native library directory from its package info.
     * Called once from {@link CotForwarderLifecycle}'s constructor.
     */
    synchronized static public void init(final Context context) {
        if (ndl == null) {
            try {
                ndl = context.getPackageManager()
                        .getApplicationInfo(context.getPackageName(),
                                0).nativeLibraryDir;
            } catch (Exception e) {
                throw new IllegalArgumentException(
                        "native library loading will fail, unable to grab the nativeLibraryDir from the package name");
            }
        }
    }

    /**
     * Load a native library by its base name (e.g. "foo" -> libfoo.so) from the
     * plugin's native dir. No-op if the file does not exist. Requires {@link #init}.
     */
    public static void loadLibrary(final String name) {
        if (ndl != null) {
            final String lib = ndl + File.separator
                    + System.mapLibraryName(name);
            if (new File(lib).exists()) {
                System.load(lib);
            }
        } else {
            throw new IllegalArgumentException("NativeLoader not initialized");
        }
    }
}
