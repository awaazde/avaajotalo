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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map.Entry;

import org.otalo.ao.client.Broadcasts.Images;
import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Prompt;
import org.otalo.ao.client.model.Survey;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.ui.Widget;

/**
 * A wrapper class for Forums to be able to act on their widget
 * representation in the interface.
 * 
 * @author dsc
 *
 */
public class SurveyWidget implements ClickHandler{
	private Tree tree;
	private TreeItem root;
	private HTML rootHTML;
	private Composite parent;
	private HashMap<HTML,Prompt> promptMap = new HashMap<HTML, Prompt>();
	private HashMap<HTML,TreeItem> leaves = new HashMap<HTML, TreeItem>();
	
	public SurveyWidget(Survey s, List<Prompt> prompts, Images images, Composite parent)
	{
		this.parent = parent;
		
		tree = new Tree(images);
		rootHTML = imageItemHTML(images.inbox(), s.getName());
    root = new TreeItem(rootHTML);
    tree.addItem(root);
    
    tree.addSelectionHandler(new SelectionHandler<TreeItem>() {

			public void onSelection(SelectionEvent<TreeItem> event) {
				TreeItem item = event.getSelectedItem();
				
				if (promptMap.containsKey(item))
				{
					Prompt p = promptMap.get(item);
					Messages.get().displaySurveyInput(p, 0);
				}
			}
		});
    
		HTML promptHTML;
		TreeItem prompt;
		String pName;
    for (Prompt p : prompts)
		{
			pName = p.getName() != null ? p.getName() : "Prompt " + p.getOrder(); 
			promptHTML = imageItemHTML(images.responses(), pName);
			prompt = new TreeItem(promptHTML);
			promptMap.put(promptHTML, p);
			leaves.put(promptHTML, prompt);
			root.addItem(prompt);
		}
    
	}
	
	
//	private void loadSurveys(List<Prompt> prompts)
//	{
//		Survey current=null, s;
//		Tree surveyTree;
//		HTML surveyTreeHTML, promptHTML;
//		TreeItem surveyRoot=null, prompt;
//		String pName;
//		for (Prompt p : prompts)
//		{
//			s = p.getSurvey();
//			
//			// ASSUMPTION: Prompts come in ordered by associated survey
//			if (current == null || !current.getId().equals(s.getId()))
//			{
//				current = s;
//				surveyTree = new Tree(images);
//				surveyTreeHTML = imageItemHTML(images.inbox(), s.getName());
//				surveyRoot = new TreeItem(surveyTreeHTML);
//				surveyTree.addItem(surveyRoot);
//				surveyTrees.put(surveyTreeHTML, surveyTree);
//				root.addItem(new TreeItem(surveyTree));
//			}
//
//			pName = p.getName() != null ? p.getName() : "Prompt " + p.getOrder(); 
//			promptHTML = imageItemHTML(images.responses(), pName);
//			prompt = new TreeItem(promptHTML);
//			promptMap.put(promptHTML, p);
//			leaves.put(promptHTML, prompt);
//			surveyRoot.addItem(prompt);
//		}
//	}
//	

  /**
   * Generates HTML for a tree item with an attached icon.
   * 
   * @param imageProto the image prototype to use
   * @param title the title of the item
   * @return the resultant HTML
   */
  private HTML imageItemHTML(ImageResource res, String title) {
  	AbstractImagePrototype imageProto = AbstractImagePrototype.create(res);
    HTML label = new HTML(imageProto.getHTML() + " " + title);
    label.addClickHandler(this);
  	label.addClickHandler((ClickHandler)parent);
  	return label;
  }
	
	public Widget getWidget()
	{
		return tree;
	}
	
	public void close()
	{
		tree.setSelectedItem(null);
		root.setState(false);
	}
	
	public boolean contains(Object w)
	{
		return w == rootHTML || promptMap.containsKey(w);
	}
	
	public void selectFirst()
	{
		root.setState(true);		
		TreeItem firstPrompt = root.getChild(0);
		tree.setSelectedItem(firstPrompt);
		root.setState(true);
		
		HTML leaf = null;
		for (Entry<HTML, TreeItem> entry : leaves.entrySet()) {
      if (entry.getValue().equals(firstPrompt)) {
          leaf = entry.getKey();
          break;
      }
		}
		
		if (leaf != null)
		{
			Prompt p = promptMap.get(leaf);
			Messages.get().displaySurveyInput(p, 0);
		}
	}

	public void onClick(ClickEvent event) {
		Object sender = event.getSource();
		
		if (sender == rootHTML)
		{
			selectFirst();
		}
		else if (promptMap.containsKey(sender))
		{
			tree.setSelectedItem(null);
			TreeItem leaf = leaves.get(sender);
			leaf.getTree().setSelectedItem(leaf);
			Prompt p = promptMap.get(sender);
			Messages.get().displaySurveyInput(p, 0);
		}
	}
	
}
