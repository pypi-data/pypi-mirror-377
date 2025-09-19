import re
import anim

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QDockWidget, QVBoxLayout, QLabel

import anim

class information:
    
  # ────────────────────────────────────────────────────────────────────────
  def __init__(self, window, width=0.25):

    # ─── Definitions ───────────────────────────

    # Set window
    self.window:anim.window = window

    # Dock width
    self.width = width

    # Display state
    self._display = False

    # Strings
    self.time = ''
    self.html = ''

    # Formating options
    self.show_steps = True
    self.show_time = True

    # ─── QWidgets ──────────────────────────────

    # ─── Dock

    self.dock = QDockWidget('', self.window)
    self.dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    self.window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
    
    '''Custom size hints, minimum and maximum sizes and size policies
    should be implemented in the child widget'''

    # self.dock.setWindowTitle('dock title')

    # ─── Vertical layout

    self.dock.setWidget(QWidget())
    self.layout = QVBoxLayout(self.dock.widget())
       
    # ─── Label

    self.label = QLabel()
    self.label.setWordWrap(True)
    self.layout.addWidget(self.label)

    # ─── Canva

    self.canva = anim.plane.canva(self.window, display_boundaries = False)
    self.layout.addWidget(self.canva.view)

    # Strech element (useful if there is no canva)
    # self.layout.addStretch()

  # ────────────────────────────────────────────────────────────────────────
  def setWidth(self, windowHeight):

    width = int(self.width*windowHeight)
    self.dock.widget().setMinimumWidth(width)
    self.dock.widget().setMaximumWidth(width)

    return width

  # ────────────────────────────────────────────────────────────────────────
  def display(self, state='toggle'):
    '''
    Defines if the dock is displayed or not
    '''

    # Display state
    if state=='toggle':
      self._display = not self._display
    else:
      self._display = state

    # Set visibility
    self.dock.setVisible(self._display)

    # Update window size
    self.window.setWindowSize()

  # ────────────────────────────────────────────────────────────────────────
  def setTime(self, signal):
    '''
    Format time string for display
    '''

    # Colors
    match self.window.style:
      case 'white'|'light': t_color = 'grey'
      case 'dark': t_color = 'lightgrey'

    match signal.type:

      case 'show' | 'update':

        step = signal.time.step if hasattr(signal, 'time') else 0
        time = signal.time.time if hasattr(signal, 'time') else 0
    
        s = ''
        if self.show_steps and self.show_time:
          s += '<table width="100%"><tr><td align=center>step</td><td align=center>time</td></tr><tr>'
          s += f'<th align=center style="color:{t_color};">{step}</th>'
          s += f'<th align=center style="color:{t_color};">{time:.02f} sec</th>'
          s += '</tr></table><hr style="background-color:grey;">'

        elif self.show_steps:
          s += '<table width="100%"><tr><td align=center>step</td></tr><tr>'
          s += f'<th align=center style="color:{t_color};">{step}</th>'
          s += '</tr></table><hr style="background-color:grey;">'

        elif self.show_time:
          s += '<table width="100%"><tr><td align=center>time</td></tr><tr>'
          s += f'<th align=center style="color:{t_color};">{time:.02f} sec</th>'
          s += '</tr></table><hr style="background-color:grey;">'

        self.time = s
        self.setHtml()

  # ────────────────────────────────────────────────────────────────────────
  def setHtml(self, html=None):

    if html is not None:
      self.html = html

    self.label.setText('<html>' + self.time + self.html + '</html>')