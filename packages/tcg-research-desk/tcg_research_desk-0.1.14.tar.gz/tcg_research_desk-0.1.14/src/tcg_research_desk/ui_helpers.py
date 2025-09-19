import param
import panel as pn

class HTMLRadioIconGroup(pn.widgets.Widget):
    """A Panel widget that behaves like RadioButtons but with HTML labels and toggle icons."""
    
    options = param.List(default=[], doc="List of option values (keys).")
    html_options = param.List(default=[], doc="List of option HTML labels (values).")
    value = param.Parameter(default=None, doc="Currently selected option (or None).")
    
    # Widget appearance parameters
    icon = param.String(default="eye", doc="Icon to use for toggle buttons")
    icon_size = param.String(default="2em", doc="Size of the toggle icons")
    
    _widget_type = pn.Column  # This makes it a composite widget
    
    def __init__(self, **params):
        super().__init__(**params)
        self._toggle_icons = []
        self._html_panes = []
        self._rows = []
        self._setup_widget()

    def _setup_widget(self):
        """Initialize the widget layout."""
        self._widget = pn.Column(width=self.width, height=self.height)
        self._update_options()
        
    def _make_toggle_callback(self, idx):
        """Create callback for toggle icon at given index."""
        def callback(event):
            if event.new:
                # Deselect all others and select this one
                self.value = self.options[idx]
            else:
                # Only allow deselecting if this was the selected one
                if self.value == self.options[idx]:
                    self.value = None
        return callback
    
    def update_options(self, options, html_options):
        """Update both options and html_options atomically to avoid race conditions."""

        if len(options) != len(html_options):
            raise ValueError(f"options and html_options are not the same length ({len(options)=}, {len(html_options)=})")
        
        with param.parameterized.batch_call_watchers(self):
            self.options = options
            self.html_options = html_options
        # Force update after batch is complete
        self._update_options()
        
    def _update_options(self):
        """Update the widget when options change."""
        # Clear existing components
        self._widget.clear()
        self._toggle_icons.clear()
        self._html_panes.clear()
        self._rows.clear()
        
        # Create new components
        for idx, (opt, html) in enumerate(zip(self.options, self.html_options)):
            html_pane = pn.pane.HTML(html, margin=(5, 0, 5, 10))
            toggle = pn.widgets.ToggleIcon(
                value=(opt == self.value),
                icon=self.icon,
                size=self.icon_size,
                sizing_mode=None,
                margin=(5, 10, 5, 0)
            )
            toggle.param.watch(self._make_toggle_callback(idx), 'value')
            
            row = pn.Row(toggle, html_pane, align="center")
            
            self._toggle_icons.append(toggle)
            self._html_panes.append(html_pane)
            self._rows.append(row)
            self._widget.append(row)

    @param.depends('value', watch=True)
    def _sync_toggle_states(self):
        """Update toggle icon states when value changes."""
        for idx, opt in enumerate(self.options):
            if idx < len(self._toggle_icons):
                selected = (opt == self.value)
                # Only update if different to avoid infinite loops
                if self._toggle_icons[idx].value != selected:
                    self._toggle_icons[idx].value = selected

    @param.depends('options', 'html_options', watch=True)
    def _on_options_change(self):
        """Re-create widget when options change."""
        self._update_options()

    @param.depends('icon', 'icon_size', watch=True) 
    def _on_appearance_change(self):
        """Update icon appearance when parameters change."""
        for toggle in self._toggle_icons:
            toggle.icon = self.icon
            toggle.size = self.icon_size

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """Return the bokeh model for this widget."""
        return self._widget._get_model(doc, root, parent, comm)

    def _cleanup(self, root=None):
        """Clean up the widget."""
        self._widget._cleanup(root)

    def __panel__(self):
        """Return the panel object for display."""
        return self._widget