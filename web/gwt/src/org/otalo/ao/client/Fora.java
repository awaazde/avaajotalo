/*
 * Copyright 2007 Google Inc.
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
import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.ImageBundle;
import com.google.gwt.user.client.ui.TreeImages;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * A panel of fora, each presented as a tree.
 */
public class Fora extends Composite implements JSONRequester, ClickHandler {
  private ArrayList<ForumWidget> widgets = new ArrayList();
	
	/**
   * Specifies the images that will be bundled for this Composite and specify
   * that tree's images should also be included in the same bundle.
   */
  public interface Images extends ImageBundle, TreeImages {
    AbstractImagePrototype inbox();
    
    AbstractImagePrototype home();

    AbstractImagePrototype drafts();
    
    AbstractImagePrototype sent();
    
    @Resource("noimage.png")
    AbstractImagePrototype treeLeaf();
  }

  private Images images;
  private VerticalPanel p;

  /**
   * Constructs a new list of forum widgets with a bundle of images.
   * 
   * @param images a bundle that provides the images for this widget
   */
  public Fora(Images images) {
	  this.images = images;
	  p = new VerticalPanel();
		// Get fora
		JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.FORUM, this);
	  
	  initWidget(p);
  }


  public void dataReceived(List<JSOModel> models)
  {
  	//pass fora
  	List<Forum> fora = new ArrayList<Forum>();
  	
  	for (JSOModel model : models)
  	{
  		fora.add(new Forum(model));
  	}
  	
  	loadFora(fora);
  }


	private void loadFora(List<Forum> fora)
	{
		
		for (int i = 0; i < fora.size(); ++i) 
		{
			Forum f = fora.get(i);
			ForumWidget w = new ForumWidget(f, images, this);
	    
	    p.add(w.getWidget());
			widgets.add(w);
		}
		
		// Hackish: for initialization
    widgets.get(0).selectMain();
	}
	
	public void setFolder(Forum f, MessageStatus status)
	{
		for (ForumWidget w : widgets)
		{
			w.setFolder(f, status);
		}
	}
	
	public void setFolderResponses(Forum f)
	{
		for (ForumWidget w : widgets)
		{
			w.setFolderResponses(f);
		}
	}


	/**
	 * This is for clicked tree items. Unselect all other ones
	 * and collapse their trees
	 * @param event
	 */
	public void onClick(ClickEvent event) {
		Object source = event.getSource();
		for (ForumWidget w : widgets)
		{
			if (!w.contains(source))
				w.close();
		}
		
	}
	
	
}
