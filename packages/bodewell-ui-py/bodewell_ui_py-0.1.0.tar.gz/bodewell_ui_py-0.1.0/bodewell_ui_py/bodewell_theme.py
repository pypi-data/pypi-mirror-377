# This theme is designed to replicate the Bodewell design system for use with
# dash-mantine-components. It is derived from the tailwind.preset.js in the @bodewell/ui library.

BODEWELL_THEME = {
    "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji'",
    "primaryColor": "blue",
    "colors": {
        "blue": [
            "#EBF4FF",
            "#D5E8FF",
            "#ADCFFF",
            "#87B5FF",
            "#609BFF",
            "#3981FF",
            "#1E6AFF",  # Primary shade for components
            "#0A58E0",
            "#0048B8",
            "#003A94"
        ],
        "gray": [
            "#f8f9fa", "#f1f3f5", "#e9ecef", "#dee2e6",
            "#ced4da", "#adb5bd", "#868e96", "#495057",
            "#343a40", "#212529",
        ],
    },
    "headings": {
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji'",
        "fontWeight": "600",
    },
    "defaultRadius": "md",
}