package core.http;

import core.http.handlers.JsonArrayHandler;

import java.io.IOException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.List;

import com.ning.http.client.AsyncHttpClient;
import com.ning.http.client.Response;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** Represents a connection to the CORE HTTP daemon. */
public class Daemon {
    public static final String DEFAULT_ADDRESS = "http://localhost:8080";

    public interface SessionHandler {
        void onSessionReceived(Session session);
    }
    public interface SessionListHandler {
        void onSessionListReceived(List<Session> sessions);
    }

    /** Connect to the daemon with the default URL. */
    public Daemon() {
        this(Daemon.DEFAULT_ADDRESS);
    }

    public Daemon(String url) {
        this.url = url;
    }

    /** Request a list of sessions from the daemon. */
    public void sessions(SessionListHandler handler) {
        AsyncHttpClient client = new AsyncHttpClient();
        client.prepareGet(this.url).execute(new JsonArrayHandler());

        Response response = future.get();

        System.out.println(response.getResponseBody());

        return null;
    }

    private class SessionListJsonHandler extends JsonArrayHandler {
        public SessionListJsonHandler(SessionListHandler handler) {
            this.handler = handler;
        }

        @Override
        public JSONArray onCompleted() {
            JSONArray array = super.onCompleted();

            List<Session> sessions = new ArrayList<Session>();
            for (int i = 0; i < array.length(); i++) {
                try {
                    JSONObject json = array.getJSONObject(i);
                } catch (JSONException e) {
                    System.err.println("Invalid JSON object at index " + i);
                    continue;
                }
                sessions.add(new Session(Daemon.this.url, json));
            }

            this.handler.onSessionListReceived(sessions);
        }

        private final SessionListHandler handler;
    }

    private final String url;
}
