package core.http.handlers;

import java.io.ByteArrayOutputStream;
import java.util.List;

import com.ning.http.client.AsyncHandler;
import com.ning.http.client.HttpResponseBodyPart;
import com.ning.http.client.HttpResponseHeaders;
import com.ning.http.client.HttpResponseStatus;
import com.ning.http.client.FluentCaseInsensitiveStringsMap;

public abstract class AbstractJsonHandler<T> implements AsyncHandler<T> {
    public AsyncHandler.STATE onStatusReceived(HttpResponseStatus status) {
        return AsyncHandler.STATE.CONTINUE;
    }

    public AsyncHandler.STATE onHeadersReceived(HttpResponseHeaders headers) {
        FluentCaseInsensitiveStringsMap map = headers.getHeaders();

        if (map.containsKey("Content-Type")) {
            List<String> values = map.get("Content-Type");
            if (values.contains("application/json")) {
                return AsyncHandler.STATE.CONTINUE;
            }
        }
        System.err.println("No JSON Content-Type");
        return AsyncHandler.STATE.ABORT;
    }

    public AsyncHandler.STATE onBodyPartReceived(HttpResponseBodyPart part) {

        return AsyncHandler.STATE.CONTINUE;
    }

    public void onThrowable(Throwable t) {
        System.err.println("Error thrown");
    }

    public abstract T onCompleted();

    protected final ByteArrayOutputStream body = new ByteArrayOutputStream();
}

