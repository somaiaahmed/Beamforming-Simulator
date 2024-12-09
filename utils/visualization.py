import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg

class BeamformingVisualizer:
    def __init__(self):
        # Configuration for visualization styles
        self.plot_config = {
            'line_color': 'blue',
            'line_width': 2,
            'background_color': 'white'
        }
    
    def plot_array_response(self, theta, array_factor, ax=None):
        """
        Plot array response (array factor) vs angle
        
        Args:
            theta (np.array): Angle values in radians
            array_factor (np.array): Array factor values
            ax (matplotlib.axes.Axes, optional): Axes to plot on
        
        Returns:
            matplotlib.axes.Axes: Plotted axes
        """
        if ax is None:
            _, ax = plt.subplots()
        
        # Convert theta to degrees
        theta_deg = np.rad2deg(theta)
        
        ax.plot(theta_deg, array_factor, 
                color=self.plot_config['line_color'], 
                linewidth=self.plot_config['line_width'])
        
        ax.set_xlabel('Angle (degrees)')
        ax.set_ylabel('Array Factor')
        ax.set_title('Array Response')
        ax.grid(True)
        
        return ax
    
    def plot_beam_profile(self, data, ax=None):
        """
        Plot beam profile intensity
        
        Args:
            data (np.array): Beam profile intensity data
            ax (matplotlib.axes.Axes, optional): Axes to plot on
        
        Returns:
            matplotlib.axes.Axes: Plotted axes
        """
        if ax is None:
            _, ax = plt.subplots(polar=True)
        
        # Polar plot of beam profile
        ax.plot(data['angles'], data['intensities'], 
                color=self.plot_config['line_color'])
        
        ax.set_title('Beam Profile')
        return ax
    
    def generate_heatmap(self, data, title='Beamforming Heatmap'):
        """
        Generate a heatmap of beamforming data
        
        Args:
            data (np.array): 2D data for heatmap
            title (str, optional): Heatmap title
        
        Returns:
            matplotlib.figure.Figure: Heatmap figure
        """
        fig, ax = plt.subplots()
        im = ax.imshow(data, cmap='viridis', aspect='auto')
        plt.colorbar(im, ax=ax)
        ax.set_title(title)
        return fig
    
    def interactive_pyqtgraph_plot(self, data):
        """
        Create an interactive plot using pyqtgraph
        
        Args:
            data (dict): Data for plotting
        
        Returns:
            pg.PlotWidget: Interactive plot widget
        """
        plot_widget = pg.PlotWidget()
        
        # Plot data
        plot_widget.plot(data['x'], data['y'])
        
        # Enable mouse interactions
        plot_widget.setMouseEnabled(x=True, y=True)
        plot_widget.enableAutoRange()
        
        return plot_widget