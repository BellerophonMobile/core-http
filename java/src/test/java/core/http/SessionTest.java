package core.http;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

public class SessionTest extends TestCase {
    public SessionTest(String testName) {
        super(testName);
    }

    public static Test suite() {
        return new TestSuite(SessionTest.class);
    }

    public void testApp() {
        assertTrue(true);
    }
}
