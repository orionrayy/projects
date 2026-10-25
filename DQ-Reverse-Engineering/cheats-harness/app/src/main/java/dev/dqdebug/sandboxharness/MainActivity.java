package dev.dqdebug.sandboxharness;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public final class MainActivity extends Activity {
    private static final int BG = Color.rgb(14, 18, 27);
    private static final int PANEL = Color.rgb(25, 32, 45);
    private static final int BORDER = Color.rgb(53, 65, 83);
    private static final int ACCENT = Color.rgb(93, 178, 255);
    private static final int TEXT = Color.rgb(236, 241, 249);
    private static final int MUTED = Color.rgb(154, 168, 188);
    private static final int WARN = Color.rgb(255, 203, 102);
    private static final String CATALOG_ASSET = "debug_cheats_catalog_v39.json";

    private final List<CatalogEntry> catalog = new ArrayList<>();
    private final List<String> categories = new ArrayList<>();
    private final Set<String> favorites = new HashSet<>();
    private SandboxState state;
    private LinearLayout content;
    private LinearLayout categoryBar;
    private TextView countText;
    private TextView stagedText;
    private TextView eventLogText;
    private String currentCategory = "All";
    private String query = "";
    private int visibleCount;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        try {
            loadCatalog();
            state = new SandboxState(catalog);
            buildUi();
        } catch (Exception error) {
            showCatalogError(error);
        }
    }

    private void loadCatalog() throws Exception {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (InputStream input = getAssets().open(CATALOG_ASSET)) {
            byte[] buffer = new byte[8192];
            int n;
            while ((n = input.read(buffer)) >= 0) bytes.write(buffer, 0, n);
        }
        JSONObject root = new JSONObject(new String(bytes.toByteArray(), StandardCharsets.UTF_8));
        JSONArray categoryArray = root.getJSONArray("categories");
        JSONArray cheatArray = root.getJSONArray("cheats");
        int declaredCount = root.getInt("count");
        if (declaredCount != 222 || cheatArray.length() != 222 || categoryArray.length() != 14) {
            throw new IllegalStateException("Expected 222 entries and 14 categories; found "
                    + cheatArray.length() + " entries and " + categoryArray.length() + " categories.");
        }
        Set<String> seenIds = new HashSet<>();
        for (int i = 0; i < categoryArray.length(); i++) categories.add(categoryArray.getString(i));
        for (int i = 0; i < cheatArray.length(); i++) {
            CatalogEntry entry = CatalogEntry.fromJson(cheatArray.getJSONObject(i));
            if (!seenIds.add(entry.id)) throw new IllegalStateException("Duplicate stable ID: " + entry.id);
            if (!categories.contains(entry.category)) throw new IllegalStateException("Unknown category: " + entry.category);
            catalog.add(entry);
        }
        if (seenIds.size() != 222) throw new IllegalStateException("Catalog stable IDs are not unique.");
    }

    private void buildUi() {
        ScrollView pageScroll = new ScrollView(this);
        pageScroll.setFillViewport(true);
        pageScroll.setBackgroundColor(BG);
        LinearLayout page = vertical();
        page.setPadding(dp(14), dp(14), dp(14), dp(28));
        pageScroll.addView(page);
        setContentView(pageScroll);

        LinearLayout mast = panel();
        mast.addView(text("DQ MODKIT  /  ANDROID HARNESS 0.19", 11, ACCENT, true));
        TextView title = text("Cheats Sandbox", 29, TEXT, true);
        title.setPadding(0, dp(5), 0, dp(2));
        mast.addView(title);
        mast.addView(text("222-item catalog · 14 categories · searchable and scrollable", 13, MUTED, false));
        page.addView(mast, marginBottom());

        LinearLayout status = panel();
        status.setBackgroundColor(Color.rgb(48, 39, 25));
        status.addView(text("GAME LINK  •  DISCONNECTED", 13, WARN, true));
        TextView note = text("This is a standalone UI/controller harness. It does not modify Dungeon Quest, native engine state, player stats, IAP, saves, cloud data, achievements, or leaderboards.", 13, TEXT, false);
        note.setPadding(0, dp(5), 0, 0);
        status.addView(note);
        page.addView(status, marginBottom());

        page.addView(text("Sandbox profiles · local drafts only", 16, TEXT, true), marginBottomSmall());
        LinearLayout presets = horizontal();
        presets.addView(button("Baseline", v -> applyPreset(SandboxState.Preset.BASELINE)), weighted());
        presets.addView(button("Power preview", v -> applyPreset(SandboxState.Preset.POWER_PREVIEW)), weighted());
        presets.addView(button("Diagnostics", v -> applyPreset(SandboxState.Preset.DIAGNOSTICS)), weighted());
        page.addView(presets, marginBottomSmall());

        LinearLayout actions = horizontal();
        actions.addView(button("Undo", v -> undo()), weighted());
        actions.addView(button("Reset", v -> reset()), weighted());
        actions.addView(button("Export JSON", v -> exportJson(false)), weighted());
        actions.addView(button("Share", v -> exportJson(true)), weighted());
        page.addView(actions, marginBottomSmall());

        EditText search = new EditText(this);
        search.setSingleLine(true);
        search.setTextSize(15);
        search.setTextColor(TEXT);
        search.setHintTextColor(MUTED);
        search.setHint("Search name, description, stable ID, or tag…");
        search.setPadding(dp(12), dp(8), dp(12), dp(8));
        search.setBackground(roundRect(PANEL, BORDER, 12));
        page.addView(search, marginBottomSmall());
        search.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                query = s == null ? "" : s.toString().trim().toLowerCase(Locale.ROOT);
                renderEntries();
            }
            @Override public void afterTextChanged(Editable s) {}
        });

        HorizontalScrollView categoryScroll = new HorizontalScrollView(this);
        categoryScroll.setHorizontalScrollBarEnabled(false);
        categoryBar = horizontal();
        addCategoryButton("All");
        addCategoryButton("Favorites");
        addCategoryButton("Active");
        for (String category : categories) addCategoryButton(category);
        categoryScroll.addView(categoryBar);
        page.addView(categoryScroll, marginBottomSmall());

        countText = text("", 13, ACCENT, true);
        countText.setPadding(dp(2), dp(4), dp(2), dp(4));
        page.addView(countText, marginBottomSmall());
        stagedText = text("", 12, MUTED, false);
        page.addView(stagedText, marginBottomSmall());

        content = vertical();
        page.addView(content, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        LinearLayout eventPanel = panel();
        eventPanel.addView(text("Recent local event log", 15, TEXT, true));
        eventLogText = text("", 11, MUTED, false);
        eventLogText.setPadding(0, dp(6), 0, 0);
        eventPanel.addView(eventLogText);
        page.addView(eventPanel, marginTop());

        renderEntries();
    }

    private void addCategoryButton(String label) {
        Button button = button(label, v -> {
            currentCategory = label;
            renderEntries();
            refreshCategoryButtons();
        });
        button.setTag("category:" + label);
        button.setTextSize(12);
        button.setPadding(dp(10), dp(6), dp(10), dp(6));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, dp(42));
        lp.setMargins(0, 0, dp(6), 0);
        categoryBar.addView(button, lp);
    }

    private void refreshCategoryButtons() {
        if (categoryBar == null) return;
        for (int i = 0; i < categoryBar.getChildCount(); i++) {
            View view = categoryBar.getChildAt(i);
            if (!(view instanceof Button)) continue;
            Button button = (Button) view;
            String tag = String.valueOf(button.getTag());
            boolean active = tag.equals("category:" + currentCategory);
            button.setBackground(roundRect(active ? ACCENT : PANEL, active ? ACCENT : BORDER, 18));
            button.setTextColor(active ? BG : TEXT);
        }
    }

    private void renderEntries() {
        if (content == null || state == null) return;
        content.removeAllViews();
        int shown = 0;
        for (CatalogEntry entry : catalog) {
            if (!matches(entry)) continue;
            content.addView(buildCard(entry), marginBottomSmall());
            shown++;
        }
        visibleCount = shown;
        if (shown == 0) {
            LinearLayout empty = panel();
            empty.addView(text("No matching catalog entries.", 14, MUTED, false));
            content.addView(empty);
        }
        countText.setText("Showing " + shown + " / 222 items  ·  " + currentCategory);
        stagedText.setText(state.stagedCount() + " staged local settings · 0 runtime-connected cheats · all game effects disabled");
        refreshCategoryButtons();
        refreshEventLog();
    }

    private boolean matches(CatalogEntry entry) {
        if ("Favorites".equals(currentCategory) && !favorites.contains(entry.id)) return false;
        if ("Active".equals(currentCategory) && state.isDefault(entry.id)) return false;
        if (!"All".equals(currentCategory) && !"Favorites".equals(currentCategory)
                && !"Active".equals(currentCategory) && !entry.category.equals(currentCategory)) return false;
        if (query.isEmpty()) return true;
        String haystack = (entry.id + " " + entry.label + " " + entry.category + " "
                + entry.description + " " + entry.control + " " + entry.tags).toLowerCase(Locale.ROOT);
        return haystack.contains(query);
    }

    private LinearLayout buildCard(CatalogEntry entry) {
        LinearLayout card = vertical();
        card.setPadding(dp(12), dp(11), dp(12), dp(12));
        card.setBackground(roundRect(PANEL, BORDER, 12));

        LinearLayout heading = horizontal();
        TextView label = text(entry.label, 16, TEXT, true);
        heading.addView(label, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        Button favorite = button(favorites.contains(entry.id) ? "★" : "☆", v -> {
            if (!favorites.add(entry.id)) favorites.remove(entry.id);
            renderEntries();
        });
        favorite.setTextSize(18);
        favorite.setContentDescription(favorites.contains(entry.id) ? "Remove favorite" : "Add favorite");
        heading.addView(favorite, new LinearLayout.LayoutParams(dp(44), dp(38)));
        card.addView(heading);

        card.addView(text(entry.category + "  ·  " + entry.control.toUpperCase(Locale.ROOT)
                + "  ·  " + entry.risk.toUpperCase(Locale.ROOT), 10, ACCENT, true));
        TextView description = text(entry.description, 12, MUTED, false);
        description.setPadding(0, dp(5), 0, dp(7));
        card.addView(description);
        card.addView(text(entry.id, 10, MUTED, false));

        if ("toggle".equals(entry.control)) {
            Switch toggle = new Switch(this);
            toggle.setText("Stage local toggle");
            toggle.setTextColor(TEXT);
            toggle.setChecked(Boolean.parseBoolean(state.get(entry.id)));
            toggle.setOnCheckedChangeListener((buttonView, checked) -> {
                try { state.set(entry.id, Boolean.toString(checked)); refreshStatusOnly(); }
                catch (IllegalArgumentException ex) { toast(ex.getMessage()); renderEntries(); }
            });
            card.addView(toggle);
        } else if ("slider".equals(entry.control)) {
            card.addView(buildSlider(entry));
        } else if ("range".equals(entry.control)) {
            card.addView(buildRange(entry));
        } else if ("select".equals(entry.control)) {
            Spinner spinner = new Spinner(this);
            ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                    android.R.layout.simple_spinner_item, entry.options);
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
            spinner.setAdapter(adapter);
            String value = state.get(entry.id);
            int selected = Math.max(0, entry.options.indexOf(value));
            spinner.setSelection(selected, false);
            spinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
                private boolean initial = true;
                @Override public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
                    if (initial) { initial = false; return; }
                    try { state.set(entry.id, entry.options.get(position)); refreshStatusOnly(); }
                    catch (IllegalArgumentException ex) { toast(ex.getMessage()); }
                }
                @Override public void onNothingSelected(android.widget.AdapterView<?> parent) {}
            });
            card.addView(text("Stage local selection", 11, MUTED, false));
            card.addView(spinner);
        } else {
            if (!entry.parameterSummaries.isEmpty()) {
                for (String summary : entry.parameterSummaries) {
                    card.addView(text("Parameter · " + summary, 11, MUTED, false));
                }
            }
            Button preview = button("Preview request · no game effect", v -> {
                state.recordActionPreview(entry.id);
                refreshStatusOnly();
                toast("Preview logged. Game adapter is disconnected.");
            });
            preview.setBackground(roundRect(Color.rgb(64, 48, 25), Color.rgb(122, 91, 42), 10));
            preview.setTextColor(WARN);
            card.addView(preview);
        }

        TextView boundary = text("LOCAL DRAFT ONLY  ·  requires verified game adapter", 10, WARN, true);
        boundary.setPadding(0, dp(7), 0, 0);
        card.addView(boundary);
        return card;
    }

    private View buildSlider(CatalogEntry entry) {
        LinearLayout panel = vertical();
        double value = Double.parseDouble(state.get(entry.id));
        TextView valueText = text(format(value) + unit(entry), 13, TEXT, true);
        panel.addView(valueText);
        SeekBar seek = new SeekBar(this);
        seek.setMax(1000);
        seek.setProgress(progressFor(entry, value));
        seek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            double pending = value;
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean fromUser) {
                pending = valueFor(entry, progress);
                valueText.setText(format(pending) + unit(entry));
            }
            @Override public void onStartTrackingTouch(SeekBar bar) {}
            @Override public void onStopTrackingTouch(SeekBar bar) {
                try { state.set(entry.id, format(snap(entry, pending))); refreshStatusOnly(); }
                catch (IllegalArgumentException ex) { toast(ex.getMessage()); }
            }
        });
        panel.addView(seek);
        panel.addView(numericStepper(entry, value, valueText, seek));
        Button exact = button("Set exact value", v -> exactNumberDialog(entry, valueText, seek));
        panel.addView(exact);
        return panel;
    }

    private View numericStepper(CatalogEntry entry, double current, TextView valueText, SeekBar seek) {
        LinearLayout row = horizontal();
        for (double delta : new double[]{-10, -1, 1, 10}) {
            String label = delta < 0 ? "−" + (int) -delta : "+" + (int) delta;
            row.addView(button(label, v -> {
                double now = Double.parseDouble(state.get(entry.id));
                double next = snap(entry, Math.max(entry.min, Math.min(entry.max, now + delta)));
                try {
                    state.set(entry.id, format(next));
                    valueText.setText(format(next) + unit(entry));
                    seek.setProgress(progressFor(entry, next));
                    refreshStatusOnly();
                } catch (IllegalArgumentException ex) { toast(ex.getMessage()); }
            }), weighted());
        }
        return row;
    }

    private View buildRange(CatalogEntry entry) {
        LinearLayout panel = vertical();
        String[] initial = state.get(entry.id).split(":", -1);
        double low = Double.parseDouble(initial[0]), high = Double.parseDouble(initial[1]);
        TextView valueText = text("Min " + format(low) + "  ·  Max " + format(high) + unit(entry), 13, TEXT, true);
        panel.addView(valueText);
        panel.addView(text("Minimum", 11, MUTED, false));
        SeekBar minSeek = new SeekBar(this);
        minSeek.setMax(1000);
        minSeek.setProgress(progressFor(entry, low));
        panel.addView(minSeek);
        panel.addView(text("Maximum", 11, MUTED, false));
        SeekBar maxSeek = new SeekBar(this);
        maxSeek.setMax(1000);
        maxSeek.setProgress(progressFor(entry, high));
        panel.addView(maxSeek);

        final double[] pending = new double[]{low, high};
        SeekBar.OnSeekBarChangeListener minListener = new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                pending[0] = valueFor(entry, progress);
                if (pending[0] > pending[1]) {
                    pending[1] = pending[0];
                    maxSeek.setProgress(progressFor(entry, pending[1]));
                }
                updateRangePreview(entry, pending, valueText);
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) { commitRange(entry, pending, valueText); }
        };
        SeekBar.OnSeekBarChangeListener maxListener = new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                pending[1] = valueFor(entry, progress);
                if (pending[1] < pending[0]) {
                    pending[0] = pending[1];
                    minSeek.setProgress(progressFor(entry, pending[0]));
                }
                updateRangePreview(entry, pending, valueText);
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) { commitRange(entry, pending, valueText); }
        };
        minSeek.setOnSeekBarChangeListener(minListener);
        maxSeek.setOnSeekBarChangeListener(maxListener);
        LinearLayout exact = horizontal();
        exact.addView(button("Set min", v -> exactRangeDialog(entry, pending, valueText, minSeek, maxSeek, true)), weighted());
        exact.addView(button("Set max", v -> exactRangeDialog(entry, pending, valueText, minSeek, maxSeek, false)), weighted());
        panel.addView(exact);
        return panel;
    }

    private void exactNumberDialog(CatalogEntry entry, TextView valueText, SeekBar seek) {
        EditText edit = new EditText(this);
        edit.setInputType(android.text.InputType.TYPE_CLASS_NUMBER
                | android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL
                | android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);
        edit.setText(state.get(entry.id));
        new AlertDialog.Builder(this).setTitle("Set " + entry.label)
                .setMessage("Bounds: " + format(entry.min) + " to " + format(entry.max) + " · step " + format(entry.step))
                .setView(edit).setNegativeButton("Cancel", null)
                .setPositiveButton("Stage locally", (dialog, which) -> {
                    try {
                        state.set(entry.id, edit.getText().toString());
                        double number = Double.parseDouble(state.get(entry.id));
                        valueText.setText(format(number) + unit(entry));
                        seek.setProgress(progressFor(entry, number));
                        refreshStatusOnly();
                    } catch (Exception ex) { toast("Invalid value: " + ex.getMessage()); }
                }).show();
    }

    private void exactRangeDialog(CatalogEntry entry, double[] pending, TextView valueText,
            SeekBar minSeek, SeekBar maxSeek, boolean editMin) {
        EditText edit = new EditText(this);
        edit.setInputType(android.text.InputType.TYPE_CLASS_NUMBER
                | android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL
                | android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);
        edit.setText(format(editMin ? pending[0] : pending[1]));
        new AlertDialog.Builder(this).setTitle("Set range " + (editMin ? "minimum" : "maximum"))
                .setMessage("Bounds: " + format(entry.min) + " to " + format(entry.max)
                        + " · step " + format(entry.step))
                .setView(edit).setNegativeButton("Cancel", null)
                .setPositiveButton("Stage locally", (dialog, which) -> {
                    try {
                        double next = snap(entry, Double.parseDouble(edit.getText().toString()));
                        if (editMin) pending[0] = Math.min(next, pending[1]);
                        else pending[1] = Math.max(next, pending[0]);
                        minSeek.setProgress(progressFor(entry, pending[0]));
                        maxSeek.setProgress(progressFor(entry, pending[1]));
                        state.set(entry.id, format(pending[0]) + ":" + format(pending[1]));
                        updateRangePreview(entry, pending, valueText);
                        refreshStatusOnly();
                    } catch (Exception ex) { toast("Invalid range value: " + ex.getMessage()); }
                }).show();
    }

    private void updateRangePreview(CatalogEntry entry, double[] pending, TextView valueText) {
        valueText.setText("Min " + format(pending[0]) + "  ·  Max " + format(pending[1]) + unit(entry));
    }

    private void commitRange(CatalogEntry entry, double[] pending, TextView valueText) {
        try {
            pending[0] = snap(entry, pending[0]);
            pending[1] = snap(entry, pending[1]);
            if (pending[0] > pending[1]) pending[0] = pending[1];
            state.set(entry.id, format(pending[0]) + ":" + format(pending[1]));
            updateRangePreview(entry, pending, valueText);
            refreshStatusOnly();
        } catch (IllegalArgumentException ex) { toast(ex.getMessage()); }
    }

    private int progressFor(CatalogEntry entry, double value) {
        if (entry.max <= entry.min) return 0;
        double p = (value - entry.min) / (entry.max - entry.min);
        return (int) Math.max(0, Math.min(1000, Math.round(p * 1000.0)));
    }

    private double valueFor(CatalogEntry entry, int progress) {
        return snap(entry, entry.min + (entry.max - entry.min) * progress / 1000.0);
    }

    private double snap(CatalogEntry entry, double value) {
        double clamped = Math.max(entry.min, Math.min(entry.max, value));
        double ticks = Math.rint((clamped - entry.min) / entry.step);
        return Math.max(entry.min, Math.min(entry.max, entry.min + ticks * entry.step));
    }

    private String unit(CatalogEntry entry) {
        return entry.unit == null || entry.unit.isEmpty() ? "" : " " + entry.unit;
    }

    private String format(double value) {
        if (Math.abs(value - Math.rint(value)) < 1e-8 && Math.abs(value) < 9e15) {
            return Long.toString(Math.round(value));
        }
        String s = String.format(Locale.US, "%.6f", value);
        while (s.contains(".") && s.endsWith("0")) s = s.substring(0, s.length() - 1);
        return s.endsWith(".") ? s.substring(0, s.length() - 1) : s;
    }

    private void applyPreset(SandboxState.Preset preset) {
        state.applyPreset(preset);
        renderEntries();
        toast("Loaded local preview preset: " + preset.name());
    }

    private void undo() {
        state.undo();
        renderEntries();
    }

    private void reset() {
        state.reset();
        renderEntries();
    }

    private void exportJson(boolean share) {
        String json = state.exportJson();
        if (!share) {
            ClipboardManager manager = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
            manager.setPrimaryClip(ClipData.newPlainText("DQ Sandbox local draft", json));
            toast("Local draft JSON copied; no game state changed.");
            return;
        }
        Intent intent = new Intent(Intent.ACTION_SEND);
        intent.setType("application/json");
        intent.putExtra(Intent.EXTRA_SUBJECT, "DQ Cheats Sandbox — local draft only");
        intent.putExtra(Intent.EXTRA_TEXT, json);
        startActivity(Intent.createChooser(intent, "Share local draft JSON"));
    }

    private void refreshStatusOnly() {
        if (stagedText != null) stagedText.setText(state.stagedCount()
                + " staged local settings · 0 runtime-connected cheats · all game effects disabled");
        refreshEventLog();
    }

    private void refreshEventLog() {
        if (eventLogText == null || state == null) return;
        List<String> events = state.recentEvents(8);
        StringBuilder out = new StringBuilder();
        for (String event : events) {
            if (out.length() > 0) out.append('\n');
            out.append("• ").append(event);
        }
        eventLogText.setText(out.toString());
    }

    private void toast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }

    public int getCatalogCount() { return catalog.size(); }
    public int getVisibleCount() { return visibleCount; }
    public SandboxState getSandboxState() { return state; }

    private void showCatalogError(Exception error) {
        ScrollView scroll = new ScrollView(this);
        LinearLayout page = vertical();
        page.setPadding(dp(18), dp(18), dp(18), dp(18));
        page.setBackgroundColor(BG);
        page.addView(text("Cheats Sandbox", 28, TEXT, true));
        page.addView(text("GAME LINK  •  DISCONNECTED", 14, WARN, true));
        page.addView(text("Catalog failed closed: " + error.getMessage(), 13, TEXT, false));
        scroll.addView(page);
        setContentView(scroll);
    }

    private LinearLayout vertical() {
        LinearLayout view = new LinearLayout(this);
        view.setOrientation(LinearLayout.VERTICAL);
        return view;
    }

    private LinearLayout horizontal() {
        LinearLayout view = new LinearLayout(this);
        view.setOrientation(LinearLayout.HORIZONTAL);
        view.setGravity(Gravity.CENTER_VERTICAL);
        return view;
    }

    private LinearLayout panel() {
        LinearLayout view = vertical();
        view.setPadding(dp(13), dp(12), dp(13), dp(12));
        view.setBackground(roundRect(PANEL, BORDER, 14));
        return view;
    }

    private GradientDrawable roundRect(int color, int stroke, int radius) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(color);
        shape.setCornerRadius(dp(radius));
        shape.setStroke(dp(1), stroke);
        return shape;
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        view.setGravity(Gravity.CENTER_VERTICAL);
        return view;
    }

    private Button button(String label, View.OnClickListener click) {
        Button view = new Button(this);
        view.setText(label);
        view.setTextSize(12);
        view.setAllCaps(false);
        view.setTextColor(TEXT);
        view.setBackground(roundRect(PANEL, BORDER, 10));
        view.setOnClickListener(click);
        return view;
    }

    private LinearLayout.LayoutParams weighted() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(44), 1f);
        lp.setMargins(dp(2), 0, dp(2), 0);
        return lp;
    }

    private LinearLayout.LayoutParams marginBottom() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(10);
        return lp;
    }

    private LinearLayout.LayoutParams marginBottomSmall() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(7);
        return lp;
    }

    private LinearLayout.LayoutParams marginTop() {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(10);
        return lp;
    }

    private int dp(float value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
