package core.http;

import org.json.JSONObject;

public class Session {
    protected Session(String address, JSONObject json) {
        this.id = json.getInt("sid");
        this.name = json.getString("name");
        this.user = json.getString("user");
        this.state = json.getString("state");

        this.url = String.format("%s/sessions/%d/", self.address, self.id);
    }

    public Session(String name, String user) {
        this.name = name;
        this.user = user;
    }

    public int getId() {
        return this.id;
    }

    public String getName() {
        return this.user;
    }

    public String getUser() {
        return this.user;
    }

    public String getState() {
        return this.state;
    }

    private final int id;
    private final String name;
    private final String user;
    private final String state;

    private final String url;
}
