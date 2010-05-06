/*
 * Copyright (c) 2009 Regents of the University of California, Stanford University, and others
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package org.otalo.ao.client;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * A simple example of a dialog box.
 */
public class ConfirmDialog extends DialogBox {

  public ConfirmDialog(String message) {
    // Use this opportunity to set the dialog's caption.
    setText("About the AO admin console");

    // Create a VerticalPanel to contain the 'about' label and the 'OK' button.
    VerticalPanel outer = new VerticalPanel();

    // Create the 'about' text and set a style name so we can style it with CSS.

    HTML text = new HTML(message);
    text.setStyleName("mail-AboutText");
    outer.add(text);

    // Create the 'OK' button, along with a handler that hides the dialog
    // when the button is clicked.
    outer.add(new Button("Close", new ClickHandler() {
      public void onClick(ClickEvent event) {
        hide();
      }
    }));

    setWidget(outer);
  }

  @Override
  public boolean onKeyDownPreview(char key, int modifiers) {
    // Use the popup's key preview hooks to close the dialog when either
    // enter or escape is pressed.
    switch (key) {
      case KeyCodes.KEY_ENTER:
      case KeyCodes.KEY_ESCAPE:
        hide();
        break;
    }

    return true;
  }
}
