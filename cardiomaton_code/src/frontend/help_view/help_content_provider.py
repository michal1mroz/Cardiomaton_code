from src.frontend.help_view.tutorial_step import TutorialStep

class HelpContentProvider:
    def __init__(self, main_window):
        self.app = main_window

    def get_steps(self) -> list[TutorialStep]:
        steps = []

        simulation_window = self.app.simulation_window.ui
        topbar = self.app.topbar

        steps.append(TutorialStep(
            widget=topbar.btn_help,
            title="Interactive Help",
            description="Pauses the simulation and highlights key interface elements. Hover over items to view their descriptions. Click anywhere on the screen to exit this mode."
        ))

        steps.append(TutorialStep(
            widget=topbar.btn_theme,
            title="Interface Theme",
            description="Click to toggle between Light ☀ and Dark ☾ modes to adjust the interface brightness."
        ))

        steps.append(TutorialStep(
            widget=topbar.btn_access,
            title="Accessibility Mode",
            description="Enables a high-contrast interface with larger text to maximize readability."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.presets_layout.dropdown,
            title="Pathology Presets",
            description="Select a specific heart pathology from the database to instantly simulate the condition and observe its impact on the simulation."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.presets_layout.button,
            title="Save Preset Mode",
            description="Enters or exits the preset saving mode. Open this interface to name and store the current simulation state. Click again to save your preset, exit the input field and return to the default view."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.modification_panel.commit_button,
            title="Commit Changes",
            description="Finalizes your parameter adjustments and applies them to the simulation, instantly updating it's behavior with the new values."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.modification_panel.undo_button,
            title="Undo Changes",
            description="Reverts the simulation configuration to the state immediately before your most recent modifications."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.modification_panel.brush_slider,
            title="Brush Size",
            description="Controls the diameter of the modification brush. New parameters are applied to the areas of the heart you paint over in the modification mode. The visual highlight confirms which cells in the conduction system are going to receive the update."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.modification_panel.necrosis_switch,
            title="Necrosis Switch",
            description="Causes necrosis in the selected area. Modified cells will become dead tissue and block signal transmission once changes are applied."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.parameter_panel.scroll,
            title="Physiological Parameters",
            description="Adjust critical cell properties within biologically accurate ranges. Parameters are grouped by cell region - scroll to explore them all. Modifications affect the simulation and display a dynamic graph, visualizing the exact impact on the cell's action potential."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.player_controls.speed_dropdown,
            title="Simulation Speed",
            description="Determines how fast the simulation runs."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.player_controls.prev_button,
            title="Rewind Simulation",
            description="Moves the simulation back in time. Clicking 'Play' will resume the action from your current position in history, not the latest frame."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.player_controls.play_button,
            title="Play / Pause",
            description="Resumes or pauses the simulation. Use this to freeze the action at any moment."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.player_controls.next_button,
            title="Step Forward",
            description="Navigates forward through the timeline. Only active after previous rewinding, it does not simulate future events. To progress further in the simulation press 'Play'."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.player_controls.toggle_render_button,
            title="Display Mode",
            description="Changes the simulation coloring. Choose between observing the electrical flow (voltage) ↯ or the specific state of each cell ⏣."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.cell_inspector_container,
            title="Cell Details",
            description="Displays detailed information about the cell you selected and presents a real-time graph of its electrical potential."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.restart_button,
            title="Reset Simulation",
            description="Restores the simulation to its initial state. All your unsaved modifications will be lost."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.toggle_interaction_button,
            title="Interaction Mode",
            description="Toggles between modification and inspection modes. In modification mode, paint over the heart and adjust parameters. In inspection mode, hover or click on the conduction system to view detailed cell properties."
        ))

        steps.append(TutorialStep(
            widget=simulation_window.presets_layout.text_input,
            title="Save Your Preset",
            description="Type a name for your preset and press the '✔' button to confirm. This saves the current state of the simulation under that name, allowing you to restore this exact configuration later."
        ))

        overlay_graph = self.app.simulation_window.overlay_graph

        if overlay_graph.isVisible():
            steps.append(TutorialStep(
                widget=overlay_graph,
                title="Action Potential Preview",
                description="A dynamic chart showing the theoretical action potential for the selected cell group. As you move the sliders, the curve shifts instantly to illustrate the expected impact on the simulation."
            ))
        else:
            steps.append(TutorialStep(
                widget=simulation_window.simulation_widget,
                title="Simulation View",
                description="The background shows a sketch of the heart structure, with the conduction system displayed on top in white. During the simulation, you can observe the flow of charge here. In inspection mode, click or hover anywhere on the conduction system to learn more."
            ))

        return steps