package core.http.handlers;

import org.json.JSONArray;

public class JsonArrayHandler extends AbstractJsonHandler<JSONArray> {
    public JSONArray onCompleted() {
        return new JSONArray(this.body.toString());
    }
}
