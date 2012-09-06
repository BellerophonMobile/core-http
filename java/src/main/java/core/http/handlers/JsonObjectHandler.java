package core.http.handlers;

import org.json.JSONObject;

public class JsonObjectHandler extends AbstractJsonHandler<JSONObject> {
    public JSONObject onCompleted() {
        return new JSONObject(this.body.toString());
    }
}
