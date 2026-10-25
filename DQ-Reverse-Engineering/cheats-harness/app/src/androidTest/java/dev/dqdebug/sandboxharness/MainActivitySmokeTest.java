package dev.dqdebug.sandboxharness;

import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.TextView;

import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/** Bounded emulator smoke test for the 222-entry catalog and disconnected safety boundary. */
@RunWith(AndroidJUnit4.class)
public final class MainActivitySmokeTest {
    @Test
    public void all222CatalogControlsFilterStageAndStayDisconnected() {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                View decor = activity.getWindow().getDecorView();
                assertTextPresent(decor, "Cheats Sandbox");
                assertTextPresent(decor, "GAME LINK  •  DISCONNECTED");
                assertTextPresent(decor, "does not modify Dungeon Quest");
                assertEquals(222, activity.getCatalogCount());
                assertEquals(222, activity.getVisibleCount());

                clickCategory(activity, "Economy Lab");
                assertEquals(17, activity.getVisibleCount());
                assertTextPresent(activity.getWindow().getDecorView(), "Debug Gold Balance");

                clickCategory(activity, "Player & Survival");
                assertEquals(27, activity.getVisibleCount());
                Switch firstToggle = findFirstSwitch(activity.getWindow().getDecorView());
                assertNotNull("Player category must render interactive toggle controls", firstToggle);
                firstToggle.performClick();
                assertEquals(1, activity.getSandboxState().stagedCount());

                clickCategory(activity, "Active");
                assertEquals(1, activity.getVisibleCount());
                clickButton(activity, "Undo");
                assertEquals(0, activity.getSandboxState().stagedCount());
                assertEquals(0, activity.getVisibleCount());

                clickCategory(activity, "All");
                assertEquals(222, activity.getVisibleCount());
                EditText search = findEditTextByTag(activity.getWindow().getDecorView(), "catalog-search");
                assertNotNull("Search field must be present", search);
                search.setText("economy.currency_override");
                clickButton(activity, "Search");
                assertEquals(1, activity.getVisibleCount());
                assertTextPresent(activity.getWindow().getDecorView(), "Debug Gold Balance");
                assertTextPresent(activity.getWindow().getDecorView(), "GAME LINK  •  DISCONNECTED");
            });
        }
    }

    private static void clickCategory(MainActivity activity, String category) {
        Button button = findButtonByTag(activity.getWindow().getDecorView(), "category:" + category);
        assertNotNull("Expected clickable category: " + category, button);
        button.performClick();
    }

    private static Button findButtonByTag(View view, String tag) {
        if (view instanceof Button && tag.equals(view.getTag())) return (Button) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                Button found = findButtonByTag(group.getChildAt(i), tag);
                if (found != null) return found;
            }
        }
        return null;
    }

    private static Button findButton(View view, String label) {
        if (view instanceof Button && label.contentEquals(((Button) view).getText())) return (Button) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                Button found = findButton(group.getChildAt(i), label);
                if (found != null) return found;
            }
        }
        return null;
    }

    private static void clickButton(MainActivity activity, String label) {
        Button button = findButton(activity.getWindow().getDecorView(), label);
        assertNotNull("Expected button: " + label, button);
        button.performClick();
    }

    private static EditText findEditTextByTag(View view, String tag) {
        if (view instanceof EditText && tag.equals(view.getTag())) return (EditText) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                EditText found = findEditTextByTag(group.getChildAt(i), tag);
                if (found != null) return found;
            }
        }
        return null;
    }

    private static Switch findFirstSwitch(View view) {
        if (view instanceof Switch) return (Switch) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                Switch found = findFirstSwitch(group.getChildAt(i));
                if (found != null) return found;
            }
        }
        return null;
    }

    private static void assertTextPresent(View view, String expected) {
        assertTrue("Expected UI text containing: " + expected, containsText(view, expected));
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
