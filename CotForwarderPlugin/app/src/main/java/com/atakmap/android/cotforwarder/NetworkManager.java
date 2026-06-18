
package com.atakmap.android.cotforwarder;

import android.content.Context;
import android.content.SharedPreferences;

import com.atakmap.android.preference.AtakPreferences;
import com.atakmap.coremap.concurrent.NamedThreadFactory;
import com.atakmap.coremap.log.Log;

import java.io.OutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * All network I/O runs on a single-threaded ExecutorService ("cotfwd-net"), so we
 * NEVER touch sockets from ATAK's UI thread (no NetworkOnMainThreadException).
 *
 * <p>Supports UDP (connectionless) and TCP (one persistent connection with lazy
 * reconnect). Implements {@link SharedPreferences.OnSharedPreferenceChangeListener}
 * to reload host/port/protocol and re-open sockets when the user edits preferences —
 * without restarting ATAK.
 *
 * <p>Wire format: each message is {@code json + "\n"} encoded as UTF-8 (newline
 * framing so the receiver can split a TCP stream or a multi-line UDP datagram).
 */
public class NetworkManager
        implements SharedPreferences.OnSharedPreferenceChangeListener {

    public static final String TAG = "CotFwd.Network";

    // Preference keys (defined in res/xml/preferences.xml).
    public static final String PREF_IP = "cotfwd_ip";
    public static final String PREF_PORT = "cotfwd_port";
    public static final String PREF_PROTO = "cotfwd_proto";

    public static final String DEFAULT_IP = "192.168.42.50";
    public static final int DEFAULT_PORT = 18999;
    public static final String DEFAULT_PROTO = "UDP";

    private static final int TCP_CONNECT_TIMEOUT_MS = 4000;

    private final AtakPreferences prefs;
    private final ExecutorService io = Executors.newSingleThreadExecutor(
            new NamedThreadFactory("cotfwd-net"));

    // Config — volatile (written on the io thread / in the constructor, read on io).
    private volatile String ip = DEFAULT_IP;
    private volatile int port = DEFAULT_PORT;
    private volatile boolean tcp = false;

    // Sockets — touched ONLY on the io thread.
    private DatagramSocket udpSocket;
    private Socket tcpSocket;
    private OutputStream tcpOut;

    public NetworkManager(Context context) {
        this.prefs = AtakPreferences.getInstance(context);
        loadConfig();
        prefs.registerListener(this);
        io.execute(new Runnable() {
            public void run() {
                openUdp();
            }
        });
    }

    /**
     * Public send API. Safe to call from any thread (including UI) — the work is
     * handed off to the io executor. {@code null} payloads are ignored.
     */
    public void send(final String json) {
        if (json == null)
            return;
        io.execute(new Runnable() {
            public void run() {
                doSend(json);
            }
        });
    }

    private void loadConfig() {
        String ipv = prefs.get(PREF_IP, DEFAULT_IP);
        if (ipv != null && ipv.trim().length() > 0)
            ip = ipv.trim();

        // PanEditTextPreference and ListPreference both persist their values as
        // String, so we read the port as a String and parse it ourselves (avoids a
        // ClassCastException on getInt()).
        try {
            String portStr = prefs.get(PREF_PORT, String.valueOf(DEFAULT_PORT));
            port = Integer.parseInt(portStr.trim());
        } catch (Exception e) {
            port = DEFAULT_PORT;
        }

        String proto = prefs.get(PREF_PROTO, DEFAULT_PROTO);
        tcp = proto != null && proto.equalsIgnoreCase("TCP");

        Log.d(TAG, "konfiguracja: " + ip + ":" + port
                + " proto=" + (tcp ? "TCP" : "UDP"));
    }

    private void openUdp() {
        try {
            if (udpSocket == null || udpSocket.isClosed())
                udpSocket = new DatagramSocket();
        } catch (Exception e) {
            Log.e(TAG, "nie udalo sie otworzyc gniazda UDP", e);
        }
    }

    private void doSend(String json) {
        // Newline framing so the receiver can split stream/datagram into messages.
        final byte[] data = (json + "\n").getBytes(StandardCharsets.UTF_8);
        try {
            if (tcp) {
                ensureTcp();
                tcpOut.write(data);
                tcpOut.flush();
            } else {
                openUdp();
                udpSocket.send(new DatagramPacket(data, data.length,
                        InetAddress.getByName(ip), port));
            }
            Log.d(TAG, "wyslano (" + (tcp ? "TCP" : "UDP") + ") " + json);
        } catch (Exception e) {
            Log.e(TAG, "wysylka nieudana do " + ip + ":" + port, e);
            closeTcp(); // force a reconnect on the next attempt
        }
    }

    private void ensureTcp() throws Exception {
        if (tcpSocket != null && tcpSocket.isConnected() && !tcpSocket.isClosed())
            return;
        closeTcp();
        Socket s = new Socket();
        s.connect(new InetSocketAddress(InetAddress.getByName(ip), port),
                TCP_CONNECT_TIMEOUT_MS);
        s.setTcpNoDelay(true);
        tcpSocket = s;
        tcpOut = s.getOutputStream();
        Log.d(TAG, "polaczono TCP " + ip + ":" + port);
    }

    @Override
    public void onSharedPreferenceChanged(SharedPreferences sp, String key) {
        if (key == null)
            return;
        if (key.equals(PREF_IP) || key.equals(PREF_PORT) || key.equals(PREF_PROTO)) {
            io.execute(new Runnable() {
                public void run() {
                    loadConfig();
                    closeTcp(); // reconnect with the new parameters on next send
                    Log.d(TAG, "przeladowano ustawienia sieci bez restartu ATAK");
                }
            });
        }
    }

    private void closeTcp() {
        try {
            if (tcpOut != null)
                tcpOut.close();
        } catch (Exception ignore) {
        }
        try {
            if (tcpSocket != null)
                tcpSocket.close();
        } catch (Exception ignore) {
        }
        tcpOut = null;
        tcpSocket = null;
    }

    private void closeAll() {
        closeTcp();
        try {
            if (udpSocket != null)
                udpSocket.close();
        } catch (Exception ignore) {
        }
        udpSocket = null;
    }

    /**
     * Cleanup invoked from onDestroyImpl: unregister the prefs listener, close the
     * sockets and shut down the thread pool.
     */
    public void dispose() {
        prefs.unregisterListener(this);
        io.execute(new Runnable() {
            public void run() {
                closeAll();
            }
        });
        io.shutdown();
    }
}
