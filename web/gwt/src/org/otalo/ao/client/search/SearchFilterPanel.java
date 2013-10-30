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

import java.util.List;

import org.otalo.ao.client.JSONRequest;
import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.JSONRequester;
import org.otalo.ao.client.Messages;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.util.QueryParam;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.dom.client.KeyUpHandler;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTML;
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
public class SearchFilterPanel extends Composite implements KeyUpHandler {

	private VerticalPanel verticalPanel;
	private TextBox searchInput;
	private CustomDateBox fromDate;
	private CustomDateBox toDate;
	private SearchTagWidget tagsInput;
	private ForumList forumList;
	private AuthorFilterCriteria authorFilter;
	private MsgStatusFilterCriteria msgStatusFilter;
	private SearchQueryParamMap queryParamsMap;

	private SearchResultMsgList searchResultContainer;
	private final DateTimeFormat formatter = DateTimeFormat.getFormat("yyyy-MM-dd"); //on server side string date should be converted back to date in this format only
	private Button searchButton;
	private HTML cancelButton;


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
		searchInput.addKeyUpHandler(this);

		Label searchLbl = new Label();
		searchLbl.setText("Keywords");
		searchLbl.addStyleName("label-txt");
		searchLbl.addStyleName("search-label");

		Label mstatusLbl = new Label();
		mstatusLbl.setText("Status");
		mstatusLbl.addStyleName("label-txt");
		msgStatusFilter = new MsgStatusFilterCriteria();

		Label dateLbl = new Label();
		dateLbl.setText("From");
		dateLbl.addStyleName("label-txt");
		Label toLbl = new Label();
		toLbl.setText("To");
		toLbl.addStyleName("label-txt");
		toLbl.addStyleName("to-lbl");

		fromDate = new CustomDateBox();
		toDate = new CustomDateBox();
		fromDate.setName(AoAPI.SearchConstants.FROMDATE);
		toDate.setName(AoAPI.SearchConstants.TODATE);

		fromDate.setFormat(new DateBox.DefaultFormat(formatter));
		toDate.setFormat(new DateBox.DefaultFormat(formatter));

		fromDate.addStyleName("date-txt");
		toDate.addStyleName("date-txt");

		Label tagLbl = new Label();
		tagLbl.setText("Tags");
		tagLbl.addStyleName("label-txt");
		tagLbl.addStyleName("tag-label");
		tagsInput = new SearchTagWidget(false, false);
		tagsInput.setWidth("255px");
		tagsInput.loadTags();

		Label forumLbl = new Label();
		forumLbl.setText("Forum");
		forumLbl.addStyleName("label-txt");
		forumList = new ForumList();

		Label authorLbl = new Label();
		authorLbl.setText("Search By");
		authorLbl.addStyleName("label-txt");
		authorFilter = new AuthorFilterCriteria();

		cancelButton = new HTML("<a href='javascript:;'>Cancel</a>");
		cancelButton.addStyleName("btn-cancel");

		searchButton = new Button();
		searchButton.setText("Search");
		searchButton.addStyleName("btn-search");

		ButtonClickHandler clickHandler = new ButtonClickHandler();
		searchButton.addClickHandler(clickHandler);
		cancelButton.addClickHandler(clickHandler);

		FlexTable fieldGrid = new FlexTable();
		fieldGrid.setCellSpacing(3);
		fieldGrid.setWidget(0, 0, searchLbl);
		fieldGrid.getFlexCellFormatter().setColSpan(0, 0, 2);

		fieldGrid.setWidget(1, 0, searchInput);
		fieldGrid.getFlexCellFormatter().setColSpan(1, 0, 2);

		fieldGrid.setWidget(2, 0, forumLbl);
		fieldGrid.getFlexCellFormatter().setColSpan(2, 0, 2);
		fieldGrid.setWidget(3, 0, forumList);
		fieldGrid.getFlexCellFormatter().setColSpan(3, 0, 2);
		fieldGrid.getFlexCellFormatter().addStyleName(9, 0, "dropdown");

		fieldGrid.setWidget(4, 0, mstatusLbl);
		fieldGrid.getFlexCellFormatter().setColSpan(4, 0, 2);
		fieldGrid.setWidget(5, 0, msgStatusFilter);
		fieldGrid.getFlexCellFormatter().setColSpan(5, 0, 2);

		fieldGrid.setWidget(6, 0, dateLbl);
		fieldGrid.setWidget(6, 1, toLbl);
		fieldGrid.setWidget(7, 0, fromDate);
		fieldGrid.setWidget(7, 1, toDate);

		fieldGrid.setWidget(8, 0, tagLbl);
		fieldGrid.getFlexCellFormatter().setColSpan(8, 0, 2);
		fieldGrid.setWidget(9, 0, tagsInput);
		fieldGrid.getFlexCellFormatter().setColSpan(9, 0, 2);

		fieldGrid.setWidget(10, 0, authorLbl);
		fieldGrid.getFlexCellFormatter().setColSpan(10, 0, 2);
		fieldGrid.setWidget(11, 0, authorFilter);
		fieldGrid.getFlexCellFormatter().setColSpan(11, 0, 2);

		HorizontalPanel buttonPlacer = new HorizontalPanel();
		buttonPlacer.setSpacing(8);
		
		buttonPlacer.add(cancelButton);
		buttonPlacer.add(searchButton);
		DOM.setStyleAttribute(buttonPlacer.getElement(), "cssFloat", "right");
		fieldGrid.setWidget(12, 0, buttonPlacer);
		fieldGrid.getFlexCellFormatter().setColSpan(12, 0, 2);

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
		forumList.reset();
		fromDate.setValue(null);
		toDate.setValue(null);
		setDefaults();
	}

	public void getSearchResult() {
		//always appending the current value of search box
		queryParamsMap.add(new QueryParam(searchInput.getName(), searchInput.getText()));
		
		//appending selected forums
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.FORUM, forumList.getSelectedValue()));
		
		//appending selected status
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.STATUS, msgStatusFilter.getSelectedValue()));
		
		//appending dates
		if(fromDate.getValue() != null)
			queryParamsMap.add(new QueryParam(fromDate.getName(), formatter.format(fromDate.getValue())));
		else
			queryParamsMap.add(new QueryParam(fromDate.getName(), ""));
		
		if(toDate.getValue() != null)
			queryParamsMap.add(new QueryParam(toDate.getName(), formatter.format(toDate.getValue())));
		else
			queryParamsMap.add(new QueryParam(toDate.getName(), ""));

		
		//appending selected status
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.TAG, tagsInput.getSelectedValue()));
		
		//appending selected author criteria
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.AUTHOR, authorFilter.getSelectedValue()));
		
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
	public void onKeyUp(KeyUpEvent event) {
		Object sender = event.getSource();
		if (sender == searchInput) {
			int stroke = event.getNativeKeyCode();
			if(stroke == 13) {
				//if its search button
				resetPagingInformation();
				getSearchResult();
			}
		}
	}

	public void resetPagingInformation() {
		//appending the paging info
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.PAGE_PARAM, "1"));
	}

	public void requestResultPage(String nextPageNo) {
		//adding into query map
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.PAGE_PARAM, nextPageNo));
		getSearchResult();
	}

	/**
	 * Sets the value of searchbox
	 * @param value
	 */
	public void setSearchPharse(String value, boolean isAdvanceSearch) {
		this.searchInput.setText(value);
		tagsInput.loadTags();
		resetPagingInformation();
		if(value != null && !value.isEmpty()) {
			if(!isAdvanceSearch)
				getSearchResult();
		}
	}

	private void setDefaults() {
		//adding default values for each search parameteres
		queryParamsMap.add(new QueryParam(searchInput.getName(), searchInput.getText()));
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.STATUS, ""));
		queryParamsMap.add(new QueryParam(AoAPI.SearchConstants.FORUM, ""));

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

	private class ButtonClickHandler implements ClickHandler {
		@Override
		public void onClick(ClickEvent event) {
			Object sender = event.getSource();
			if(sender == searchButton) {
				//if its search button
				resetPagingInformation();
				getSearchResult();
			}
			else if(sender == cancelButton) {
				//if its cancel button then hiding search panel
				Messages.get().hideSearchPanel();
			}
		}
	}
}
