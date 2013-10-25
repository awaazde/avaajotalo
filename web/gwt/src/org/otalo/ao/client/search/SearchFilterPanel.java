/**
  * Copyright (c) 2013 Regents of the University of California, Stanford University, and others
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
package org.otalo.ao.client.search;

import java.util.Date;
import java.util.List;

import org.otalo.ao.client.JSONRequest;
import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.JSONRequester;
import org.otalo.ao.client.Messages;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.util.QueryParam;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.datepicker.client.DateBox;

/**
 * @author nikhil
 *
 */
public class SearchFilterPanel extends Composite implements EventObserver {

	private VerticalPanel verticalPanel;
	private TextBox searchInput;
	private CustomDateBox fromDate;
	private CustomDateBox toDate;
	private SearchTagWidget tagsInput;
	private AuthorFilterCriteria authorFilter;
	private MsgStatusFilterCriteria msgStatusFilter;
	private SearchQueryParamMap queryParamsMap;
	
	private SearchResultMsgList searchResultContainer;
	private final DateTimeFormat formatter = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss"); //on server side string date should be converted back to date in this format only
	private Button searchButton;
	
	
	/**
	   * Specifies the images that will be bundled for this Composite and specify
	   * that tree's images should also be included in the same bundle.
	   */
	  public interface Images extends ClientBundle {
	    //ImageResource search();
	  }
	
	public SearchFilterPanel(SearchResultMsgList searchResultContainer) {
		//Initializing queryParams
		queryParamsMap = new SearchQueryParamMap();
		
		this.searchResultContainer = searchResultContainer;
		
		verticalPanel = new VerticalPanel();
		verticalPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_TOP);
		verticalPanel.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
		
		//Initializing other widgets
		searchInput = new TextBox();
		searchInput.setName(AoAPI.SearchConstants.SEARCH_KEYWORD);
		searchInput.setTitle(AoAPI.SearchConstants.SEARCH_KEYWORD);
		searchInput.addStyleName("input-txt");

		Label searchLbl = new Label();
		searchLbl.setText("Search Keyword:");
		searchLbl.addStyleName("label-txt");
		searchLbl.addStyleName("search-label");
		
		Label mstatusLbl = new Label();
		mstatusLbl.setText("Status:");
		mstatusLbl.addStyleName("label-txt");
		msgStatusFilter = new MsgStatusFilterCriteria(this);
		
		Label dateLbl = new Label();
		dateLbl.setText("From Date:");
		dateLbl.addStyleName("label-txt");
		Label toLbl = new Label();
		toLbl.setText("To Date:");
		toLbl.addStyleName("label-txt");
		toLbl.addStyleName("to-lbl");
		
		fromDate = new CustomDateBox();
		toDate = new CustomDateBox();
		fromDate.setName(AoAPI.SearchConstants.FROMDATE);
		toDate.setName(AoAPI.SearchConstants.TODATE);
		
		fromDate.addValueChangeHandler(new DateValueChangeHandler());
		toDate.addValueChangeHandler(new DateValueChangeHandler());
		
		fromDate.addStyleName("date-txt");
		toDate.addStyleName("date-txt");
		
		Label tagLbl = new Label();
		tagLbl.setText("Tags:");
		tagLbl.addStyleName("label-txt");
		tagLbl.addStyleName("tag-label");
		tagsInput = new SearchTagWidget(false, false, this);
		tagsInput.setWidth("252px");
		tagsInput.loadTags();

		Label authorLbl = new Label();
		authorLbl.setText("Author:");
		authorLbl.addStyleName("label-txt");
		authorFilter = new AuthorFilterCriteria(this);
		
		searchButton = new Button();
		searchButton.setText("Search");
		searchButton.addStyleName("btn-search");
		
		searchButton.addClickHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent event) {
				resetPagingInformation();
				notifyQueryChangeListener(searchInput.getName(), searchInput.getText());
			}
		});
		
		Grid fieldGrid = new Grid(12, 1);
		fieldGrid.setCellSpacing(3);
		fieldGrid.setWidget(0, 0, searchLbl);
		HorizontalPanel searchBoxPanel = new HorizontalPanel();
		searchBoxPanel.setSpacing(4);
		searchBoxPanel.add(searchInput);
		searchBoxPanel.add(searchButton);
		fieldGrid.setWidget(1, 0, searchBoxPanel);
		
		fieldGrid.setWidget(2, 0, mstatusLbl);
		fieldGrid.setWidget(3, 0, msgStatusFilter);
		
		fieldGrid.setWidget(4, 0, dateLbl);
		fieldGrid.setWidget(5, 0, fromDate);
		fieldGrid.setWidget(6, 0, toLbl);
		fieldGrid.setWidget(7, 0, toDate);
		fieldGrid.setWidget(8, 0, tagLbl);
		fieldGrid.setWidget(9, 0, tagsInput);
		fieldGrid.setWidget(10, 0, authorLbl);
		fieldGrid.setWidget(11, 0, authorFilter);
	
		verticalPanel.add(fieldGrid);
		
		initWidget(verticalPanel);
		//setting default search fields
		setDefaults();
	}
	
	
	public void reset() {
		searchInput.setText("");
		tagsInput.reset();
		tagsInput.loadTags();
		authorFilter.reset();
		msgStatusFilter.reset();
		setDefaults();
	}

	@Override
	public void notifyQueryChangeListener(String searchProperty, String latestState) {
		//adding into query map, it will automatically prevents duplicates query parameters
		queryParamsMap.add(new QueryParam(searchProperty, latestState));
		
		//always appending the current value of search box
		queryParamsMap.add(new QueryParam(searchInput.getName(), searchInput.getText()));
		
		final SearchFilterPanel filterPanelRef = this;
		//showing the loader
		Messages.get().showLoader(true);
		
		JSONRequest request = new JSONRequest();
		request.doPost(AoAPI.SearchConstants.SEARCH, AoAPI.SearchConstants.SEARCH_PARAM + "=" + queryParamsMap.jsonString(), new JSONRequester() {
			@Override
			public void dataReceived(List<JSOModel> models) {
				//on receiving data hiding it
				Messages.get().showLoader(false);
				searchResultContainer.displayMessages(filterPanelRef, models);
			}
		});
		
	}
	
	@Override
	public void resetPagingInformation() {
		//appending the paging info
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.PAGE_PARAM, "1"));
	}
	
	public void requestResultPage(String nextPageNo) {
		notifyQueryChangeListener(AoAPI.SearchConstants.PAGE_PARAM, nextPageNo);
	}
	
	/**
	 * Sets the value of searchbox
	 * @param value
	 */
	public void setSearchPharse(String value) {
		this.searchInput.setText(value);
		tagsInput.loadTags();
		resetPagingInformation();
		if(value != null && !value.isEmpty())
			notifyQueryChangeListener(searchInput.getName(), searchInput.getText());
	}
	
	private void setDefaults() {
		//adding default values for each search parameteres
		queryParamsMap.add(new QueryParam(searchInput.getName(), searchInput.getText()));
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.STATUS, ""));
		
		if(fromDate.getValue() != null)
			queryParamsMap.add(new QueryParam(fromDate.getName(), formatter.format(fromDate.getValue())));
		else
			queryParamsMap.add(new QueryParam(fromDate.getName(), ""));
		if(toDate.getValue() != null)
			queryParamsMap.add(new QueryParam(toDate.getName(), formatter.format(toDate.getValue())));
		else
			queryParamsMap.add(new QueryParam(toDate.getName(), ""));
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.TAG, ""));
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.AUTHOR, ""));
		
		//appending the paging info
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.PAGE_PARAM, "1"));
	}
	
	/**
	 * Custom DateBox class. Extending default functionalities of DateBox + having name attribute which is missing into DateBox.
	 * @author nikhil
	 *
	 */
	private class CustomDateBox extends DateBox {
		private String name; //name should be unique and can be used to identify the object

		/**
		 * @return the name
		 */
		public String getName() {
			return name;
		}

		/**
		 * @param name the name to set
		 */
		public void setName(String name) {
			this.name = name;
		}
	}
	
	private class DateValueChangeHandler implements ValueChangeHandler<Date> {
		@Override
		public void onValueChange(ValueChangeEvent<Date> event) {
			CustomDateBox source = (CustomDateBox) event.getSource();
			resetPagingInformation();
			notifyQueryChangeListener(source.getName(), formatter.format(source.getValue()));
		}
	}
}
