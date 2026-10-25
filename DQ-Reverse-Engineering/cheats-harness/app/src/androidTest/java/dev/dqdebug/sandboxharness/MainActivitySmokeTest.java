package dev.dqdebug.sandboxharness;

import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Emulator regression smoke test for navigation and local preview controls.
 * It explicitly verifies the game adapter remains disconnected.
 */
@RunWith(AndroidJUnit4.class)
public final class MainActivitySmokeTest {

    @Test
    public void homeAndCategoryNavigationStayDisconnected() {
        try (ActivityScenario<MainActivity> scenario =
                     ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                View decor = activity.getWindow().getDecorView();
                assertTextPresent(decor, "Cheats Sandbox");
                assertTextPresent(decor, "GAME LINK  •  DISCONNECTED");
                assertTextPresent(decor, "does not modify Dungeon Quest");

                clickCategory(activity, "Economy");
                assertTextPresent(activity.getWindow().getDecorView(), "Gold multiplier");
                assertTextPresent(activity.getWindow().getDecorView(),
                        "GAME LINK  •  DISCONNECTED");

                clickCategory(activity, "World");
                assertTextPresent(activity.getWindow().getDecorView(), "No-clip (preview)");
                assertTextPresent(activity.getWindow().getDecorView(),
                        "GAME LINK  •  DISCONNECTED");

                clickCategory(activity, "Diagnostics");
                assertTextPresent(activity.getWindow().getDecorView(),
                        "Hitbox overlay (preview)");
                assertTextPresent(activity.getWindow().getDecorView(),
                        "GAME LINK  •  DISCONNECTED");

                clickCategory(activity, "Player");
                clickButton(activity, "Power preview");
                assertTextPresent(activity.getWindow().getDecorView(),
                        "GAME LINK  •  DISCONNECTED");
                clickButton(activity, "Undo");
                clickButton(activity, "Reset");
                assertTextPresent(activity.getWindow().getDecorView(), "Cheats Sandbox");
                assertTextPresent(activity.getWindow().getDecorView(),
                        "GAME LINK  •  DISCONNECTED");
            });
        }
    }

    private static void clickCategory(MainActivity activity, String category) {
        Button button = findButtonByTag(
                activity.getWindow().getDecorView(), "category:" + category);
        assertNotNull("Expected clickable category: " + category, button);
        button.performClick();
    }

    private static Button findButtonByTag(View view, String tag) {
        if (view instanceof Button && tag.equals(view.getTag())) {
            return (Button) view;
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                Button found = findButtonByTag(group.getChildAt(i), tag);
                if (found != null) return found;
            }
        }
        return null;
    }

    private static void clickButton(MainActivity activity, String label) {
        Button button = findButton(activity.getWindow().getDecorView(), label);
        assertNotNull("Expected clickable button: " + label, button);
        button.performClick();
    }

    private static Button findButton(View view, String label) {
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

    private static void assertTextPresent(View view, String expected) {
        assertTrue("Expected UI/accessibility text containing: " + expected,
                containsText(view, expected));
    }

    private static boolean containsText(View view, String expected) {
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
