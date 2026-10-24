package dev.dqdebug.sandboxharness;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.HorizontalScrollView;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class MainActivity extends Activity {
    private static final int BG = Color.rgb(14, 18, 27);
    private static final int PANEL = Color.rgb(25, 32, 45);
    private static final int ACCENT = Color.rgb(93, 178, 255);
    private static final int TEXT = Color.rgb(236, 241, 249);
    private static final int MUTED = Color.rgb(154, 168, 188);
    private static final int WARN = Color.rgb(255, 203, 102);

    private final SandboxState state = new SandboxState();
    private LinearLayout content;
    private LinearLayout categoryBar;
    private String currentCategory = "Player";
    private final List<CategoryButton> categoryButtons = new ArrayList<>();

    private static final Setting[] SETTINGS = new Setting[] {
        new Setting("Player", "player.god_mode", "God mode", "UI preview toggle; no gameplay effect.", false, 1),
        new Setting("Player", "player.infinite_health", "Infinite health", "Local preview state only.", false, 1),
        new Setting("Player", "player.infinite_mana", "Infinite mana", "Local preview state only.", false, 1),
        new Setting("Combat", "combat.freeze_enemies", "Freeze enemies", "Preview flag; no native game hook.", false, 1),
        new Setting("Combat", "combat.one_hit", "One-hit mode", "Preview flag; no native game hook.", false, 1),
        new Setting("Economy", "economy.gold_multiplier", "Gold multiplier", "Staged multiplier preview (1x–100x).", true, 100),
        new Setting("Economy", "economy.xp_multiplier", "XP multiplier", "Staged multiplier preview (1x–100x).", true, 100),
        new Setting("Economy", "loot.drop_multiplier", "Drop multiplier", "Staged multiplier preview (1x–100x).", true, 100),
        new Setting("World", "world.no_clip_preview", "No-clip (preview)", "Visual toggle only; does not change collision.", false, 1),
        new Setting("World", "world.freeze_timer_preview", "Freeze timer (preview)", "Visual toggle only; does not change game time.", false, 1),
        new Setting("Diagnostics", "diagnostics.hitboxes_preview", "Hitbox overlay (preview)", "Reserved until a verified renderer hook exists.", false, 1),
        new Setting("Diagnostics", "diagnostics.performance_overlay", "Performance overlay (local)", "Displays harness status, not game FPS.", false, 1)
    };

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        buildUi();
    }

    private void buildUi() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(BG);
        LinearLayout page = vertical();
        page.setPadding(dp(18), dp(18), dp(18), dp(28));
        scroll.addView(page);
        setContentView(scroll);

        page.addView(text("DQ MODKIT  /  BUILD 0.17", 11, ACCENT, true));
        TextView title = text("Cheats Sandbox", 29, TEXT, true);
        title.setPadding(0, dp(5), 0, dp(2));
        page.addView(title);
        page.addView(text("UI & controller build harness", 14, MUTED, false));

        LinearLayout linkCard = panel();
        linkCard.addView(text("GAME LINK  •  DISCONNECTED", 13, WARN, true));
        TextView linkNote = text("No adapter for Dungeon Quest v3.3.2.0 is installed in this APK.", 13, TEXT, false);
        linkNote.setPadding(0, dp(6), 0, 0);
        linkCard.addView(linkNote);
        page.addView(linkCard, marginBottom());

        LinearLayout warning = panel();
        warning.setBackgroundColor(Color.rgb(48, 39, 25));
        warning.addView(text("IMPORTANT: Every control here changes local preview values only. This build does not modify Dungeon Quest, player stats, IAP, saves, or native engine state.", 13, WARN, false));
        page.addView(warning, marginBottom());

        TextView presetHeading = text("Sandbox profiles", 17, TEXT, true);
        presetHeading.setPadding(0, dp(4), 0, dp(8));
        page.addView(presetHeading);
        LinearLayout presets = horizontal();
        presets.addView(button("Baseline", v -> choosePreset(SandboxState.Preset.BASELINE)), weighted());
        presets.addView(button("Power preview", v -> choosePreset(SandboxState.Preset.POWER_PREVIEW)), weighted());
        presets.addView(button("Diagnostics", v -> choosePreset(SandboxState.Preset.DIAGNOSTICS)), weighted());
        page.addView(presets, marginBottom());

        categoryBar = horizontal();
        HorizontalScrollView catScroll = new HorizontalScrollView(this);
        catScroll.setHorizontalScrollBarEnabled(false);
        catScroll.addView(categoryBar);
        page.addView(catScroll, marginBottom());

        content = vertical();
        page.addView(content, marginBottom());

        LinearLayout actions = horizontal();
        actions.addView(button("Undo", v -> { state.undo(); renderCategory(); renderEvents(findEventsPanel()); }), weighted());
        actions.addView(button("Reset", v -> { state.reset(); renderCategory(); renderEvents(findEventsPanel()); }), weighted());
        actions.addView(button("Export", v -> exportState()), weighted());
        page.addView(actions, marginBottom());

        TextView eventHeading = text("Recent local events", 17, TEXT, true);
        eventHeading.setPadding(0, dp(4), 0, dp(7));
        page.addView(eventHeading);
        LinearLayout eventPanel = panel();
        eventPanel.setTag("events");
        page.addView(eventPanel);

        rebuildCategoryButtons();
        renderCategory();
        renderEvents(eventPanel);
    }

    private void rebuildCategoryButtons() {
        categoryBar.removeAllViews();
        categoryButtons.clear();
        for (String cat : new String[]{"Player", "Combat", "Economy", "World", "Diagnostics"}) {
            Button b = button(cat, v -> {
                currentCategory = cat;
                renderCategory();
            });
            // Give category navigation a stable target distinct from same-named presets.
            b.setTag("category:" + cat);
            categoryBar.addView(b);
            categoryButtons.add(new CategoryButton(cat, b));
        }
        updateCategoryButtonStyles();
    }

    private void updateCategoryButtonStyles() {
        for (CategoryButton item : categoryButtons) {
            item.button.setTextColor(item.category.equals(currentCategory) ? BG : TEXT);
            item.button.setBackgroundTintList(android.content.res.ColorStateList.valueOf(
                    item.category.equals(currentCategory) ? ACCENT : PANEL));
        }
    }

    private void renderCategory() {
        if (content == null) return;
        content.removeAllViews();
        updateCategoryButtonStyles();
        Map<String, Integer> values = state.snapshot();
        for (Setting s : SETTINGS) {
            if (!s.category.equals(currentCategory)) continue;
            LinearLayout row = panel();
            LinearLayout heading = horizontal();
            LinearLayout labels = vertical();
            labels.addView(text(s.title, 15, TEXT, true));
            TextView desc = text(s.description, 12, MUTED, false);
            desc.setPadding(0, dp(3), 0, 0);
            labels.addView(desc);
            heading.addView(labels, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
            if (!s.range) {
                Switch toggle = new Switch(this);
                toggle.setChecked(values.get(s.id) != 0);
                toggle.setOnCheckedChangeListener((buttonView, checked) -> {
                    state.set(s.id, checked ? 1 : 0);
                    renderCategory();
                    renderEvents(findEventsPanel());
                });
                heading.addView(toggle);
                row.addView(heading);
                content.addView(row, marginBottom());
            } else {
                TextView valueText = text(values.get(s.id) + "x", 15, ACCENT, true);
                heading.addView(valueText);
                row.addView(heading);
                SeekBar slider = new SeekBar(this);
                slider.setMax(s.max - 1);
                slider.setProgress(values.get(s.id) - 1);
                slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                    int latest = values.get(s.id);
                    @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                        latest = progress + 1;
                        valueText.setText(latest + "x");
                    }
                    @Override public void onStartTrackingTouch(SeekBar seekBar) {}
                    @Override public void onStopTrackingTouch(SeekBar seekBar) {
                        state.set(s.id, latest);
                        renderCategory();
                        renderEvents(findEventsPanel());
                    }
                });
                row.addView(slider);
                content.addView(row, marginBottom());
            }
        }
    }

    private ViewGroup findEventsPanel() {
        View rootView = findViewById(android.R.id.content);
        if (!(rootView instanceof ViewGroup)) return null;
        View frameChild = ((ViewGroup) rootView).getChildAt(0);
        if (!(frameChild instanceof ScrollView)) return null;
        View pageChild = ((ScrollView) frameChild).getChildAt(0);
        if (!(pageChild instanceof ViewGroup)) return null;
        ViewGroup page = (ViewGroup) pageChild;
        for (int i = 0; i < page.getChildCount(); i++) {
            View v = page.getChildAt(i);
            if (v instanceof ViewGroup && "events".equals(v.getTag())) return (ViewGroup) v;
        }
        return null;
    }

    private void renderEvents(ViewGroup panel) {
        if (panel == null) return;
        panel.removeAllViews();
        List<String> events = state.recentEvents(5);
        for (int i = events.size() - 1; i >= 0; i--) {
            TextView line = text("• " + events.get(i), 12, MUTED, false);
            line.setPadding(0, dp(3), 0, dp(3));
            panel.addView(line);
        }
    }

    private void choosePreset(SandboxState.Preset preset) {
        state.applyPreset(preset);
        renderCategory();
        renderEvents(findEventsPanel());
    }

    private void exportState() {
        Intent send = new Intent(Intent.ACTION_SEND);
        send.setType("text/plain");
        send.putExtra(Intent.EXTRA_SUBJECT, "DQ Cheats Sandbox — local UI preview export");
        send.putExtra(Intent.EXTRA_TEXT, state.exportJson());
        startActivity(Intent.createChooser(send, "Export local preview state"));
    }

    private LinearLayout vertical() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        return layout;
    }

    private LinearLayout horizontal() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        layout.setGravity(Gravity.CENTER_VERTICAL);
        return layout;
    }

    private LinearLayout panel() {
        LinearLayout layout = vertical();
        layout.setPadding(dp(13), dp(12), dp(13), dp(12));
        layout.setBackgroundColor(PANEL);
        return layout;
    }

    private TextView text(String value, int sp, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return view;
    }

    private Button button(String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setAllCaps(false);
        b.setText(label);
        b.setTextSize(12);
        b.setTextColor(TEXT);
        b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PANEL));
        b.setMinHeight(dp(42));
        b.setPadding(dp(7), dp(3), dp(7), dp(3));
        b.setOnClickListener(listener);
        return b;
    }

    private LinearLayout.LayoutParams marginBottom() {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        p.bottomMargin = dp(10);
        return p;
    }

    private LinearLayout.LayoutParams weighted() {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        p.setMargins(dp(2), 0, dp(2), 0);
        return p;
    }

    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private static final class Setting {
        final String category, id, title, description;
        final boolean range;
        final int max;
        Setting(String category, String id, String title, String description, boolean range, int max) {
            this.category = category;
            this.id = id;
            this.title = title;
            this.description = description;
            this.range = range;
            this.max = max;
        }
    }

    private static final class CategoryButton {
        final String category;
        final Button button;
        CategoryButton(String category, Button button) { this.category = category; this.button = button; }
    }
}
