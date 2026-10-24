package dev.dqdebug.sandboxharness;

import android.test.ActivityInstrumentationTestCase2;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

/** Emulator smoke test: the UI starts, labels the game adapter disconnected, and category taps work. */
@SuppressWarnings("deprecation")
public final class MainActivitySmokeTest extends ActivityInstrumentationTestCase2<MainActivity> {
    public MainActivitySmokeTest() {
        super(MainActivity.class);
    }

    public void testHomeAndCategoryNavigationStayDisconnected() throws Exception {
        final MainActivity activity = getActivity();
        assertNotNull("MainActivity must launch", activity);
        getInstrumentation().waitForIdleSync();

        assertTextPresent(activity.getWindow().getDecorView(), "Cheats Sandbox");
        assertTextPresent(activity.getWindow().getDecorView(), "GAME LINK  •  DISCONNECTED");
        assertTextPresent(activity.getWindow().getDecorView(), "does not modify Dungeon Quest");

        clickButton(activity, "Economy");
        assertTextPresent(activity.getWindow().getDecorView(), "Gold multiplier");
        assertTextPresent(activity.getWindow().getDecorView(), "GAME LINK  •  DISCONNECTED");

        clickButton(activity, "World");
        assertTextPresent(activity.getWindow().getDecorView(), "No-clip (preview)");
        assertTextPresent(activity.getWindow().getDecorView(), "GAME LINK  •  DISCONNECTED");

        clickButton(activity, "Diagnostics");
        assertTextPresent(activity.getWindow().getDecorView(), "Hitbox overlay (preview)");
        assertTextPresent(activity.getWindow().getDecorView(), "GAME LINK  •  DISCONNECTED");
    }

    private void clickButton(final MainActivity activity, final String label) throws Exception {
        final Button[] found = new Button[1];
        getInstrumentation().runOnMainSync(new Runnable() {
            @Override public void run() {
                found[0] = findButton(activity.getWindow().getDecorView(), label);
                if (found[0] != null) found[0].performClick();
            }
        });
        assertNotNull("Expected clickable button: " + label, found[0]);
        getInstrumentation().waitForIdleSync();
    }

    private Button findButton(View view, String label) {
        if (view instanceof Button && label.contentEquals(((Button) view).getText())) {
            return (Button) view;
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                Button found = findButton(group.getChildAt(i), label);
                if (found != null) return found;
            }
        }
        return null;
    }

    private void assertTextPresent(View view, String expected) {
        assertTrue("Expected visible/accessibility text containing: " + expected,
                containsText(view, expected));
    }

    private boolean containsText(View view, String expected) {
        if (view instanceof TextView) {
            CharSequence text = ((TextView) view).getText();
            if (text != null && text.toString().contains(expected)) return true;
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                if (containsText(group.getChildAt(i), expected)) return true;
            }
        }
        return false;
    }
}
