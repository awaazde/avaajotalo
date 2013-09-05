/*
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
package org.otalo.ao.client.widget.chlist.gwt;

import static com.google.gwt.query.client.GQuery.$;

import org.otalo.ao.client.widget.chlist.client.Chosen;
import org.otalo.ao.client.widget.chlist.client.ChosenImpl;
import org.otalo.ao.client.widget.chlist.client.ChosenOptions;
import org.otalo.ao.client.widget.chlist.event.ChosenChangeEvent;
import org.otalo.ao.client.widget.chlist.event.HasAllChosenHandlers;
import org.otalo.ao.client.widget.chlist.event.HidingDropDownEvent;
import org.otalo.ao.client.widget.chlist.event.MaxSelectedEvent;
import org.otalo.ao.client.widget.chlist.event.ReadyEvent;
import org.otalo.ao.client.widget.chlist.event.ShowingDropDownEvent;
import org.otalo.ao.client.widget.chlist.event.UpdatedEvent;
import org.otalo.ao.client.widget.chlist.event.ChosenChangeEvent.ChosenChangeHandler;
import org.otalo.ao.client.widget.chlist.event.HidingDropDownEvent.HidingDropDownHandler;
import org.otalo.ao.client.widget.chlist.event.MaxSelectedEvent.MaxSelectedHandler;
import org.otalo.ao.client.widget.chlist.event.ReadyEvent.ReadyHandler;
import org.otalo.ao.client.widget.chlist.event.ShowingDropDownEvent.ShowingDropDownHandler;
import org.otalo.ao.client.widget.chlist.event.UpdatedEvent.UpdatedHandler;

import com.google.gwt.core.client.JsArrayString;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.NodeList;
import com.google.gwt.dom.client.OptionElement;
import com.google.gwt.dom.client.SelectElement;
import com.google.gwt.event.dom.client.DomEvent.Type;
import com.google.gwt.event.shared.EventHandler;
import com.google.gwt.event.shared.LegacyHandlerWrapper;
import com.google.gwt.i18n.client.HasDirection.Direction;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.web.bindery.event.shared.EventBus;
import com.google.web.bindery.event.shared.HandlerRegistration;
import com.google.web.bindery.event.shared.SimpleEventBus;

public class  ChosenListBox extends ListBox implements HasAllChosenHandlers {

    /**
     * Indicates of the ChosenListBox is supported by the current browser. If
     * not (IE6/7), we fall back on normal select element.
     *
     * @return
     */
    public static boolean isSupported() {
        return org.otalo.ao.client.widget.chlist.client.Chosen.isSupported();
    }

    /**
     * Creates a ChosenListBox widget that wraps an existing &lt;select&gt;
     * element.
     * <p/>
     * This element must already be attached to the document. If the element is
     * removed from the document, you must call
     * {@link RootPanel#detachNow(Widget)}.
     *
     * @param element the element to be wrapped
     * @return list box
     */
    public static ChosenListBox wrap(Element element) {
        assert Document.get().getBody().isOrHasChild(element);

        ChosenListBox listBox = new ChosenListBox(element);

        listBox.onAttach();
        RootPanel.detachOnWindowClose(listBox);

        return listBox;
    }

    private static String OPTGROUP_TAG = "optgroup";

    private EventBus chznHandlerManager;
    private ChosenOptions options;
    private boolean visible = true;

    /**
     * Creates an empty chosen component in single selection mode.
     */
    public ChosenListBox() {
        this(false);
    }

    /**
     * Creates an empty chosen component in single selection mode.
     */
    public ChosenListBox(ChosenOptions options) {
        this(false, options);
    }

    /**
     * Creates an empty list box. The preferred way to enable multiple
     * selections is to use this constructor rather than
     * {@link #setMultipleSelect(boolean)}.
     *
     * @param isMultipleSelect specifies if multiple selection is enabled
     */
    public ChosenListBox(boolean isMultipleSelect) {
        this(isMultipleSelect, new ChosenOptions());
    }

    /**
     * Creates an empty list box. The preferred way to enable multiple
     * selections is to use this constructor rather than
     * {@link #setMultipleSelect(boolean)}.
     *
     * @param isMultipleSelect specifies if multiple selection is enabled
     */
    public ChosenListBox(boolean isMultipleSelect, ChosenOptions options) {
        super(Document.get().createSelectElement(isMultipleSelect));
        this.options = options;
    }

    protected ChosenListBox(Element element) {
        super(element);
    }

    /**
     * Deprecated, use {@link #addChosenChangeHandler(ChosenChangeHandler)}
     * instead
     */
    @Override
    @Deprecated
    public com.google.gwt.event.shared.HandlerRegistration addChangeHandler(
            final com.google.gwt.event.dom.client.ChangeHandler handler) {
        final HandlerRegistration registration = addChosenChangeHandler(new ChosenChangeHandler() {
            public void onChange(ChosenChangeEvent event) {
                handler.onChange(null);
            }
        });

        return new LegacyHandlerWrapper(registration);
    }

    public HandlerRegistration addChosenChangeHandler(
            ChosenChangeHandler handler) {
        return ensureChosenHandlers().addHandler(ChosenChangeEvent.getType(),
                handler);
    }

    /**
     * Adds a group at the end of the list box.
     *
     * @param label the text of the group to be added
     */
    public void addGroup(String label) {
        insertGroup(label, -1);
    }

    /**
     * Adds a group at the end of the list box.
     *
     * @param label the text of the group to be added
     * @param groupId the id for the optgroup element
     */
    public void addGroup(String label, String groupId) {
        insertGroup(label, groupId, -1);
    }

    public HandlerRegistration addHidingDropDownHandler(
            HidingDropDownHandler handler) {
        return ensureChosenHandlers().addHandler(HidingDropDownEvent.getType(),
                handler);
    }

    /**
     * Adds an item to the last optgroup of the list box.
     *
     * @param item the text of the item to be added
     */
    public void addItemToGroup(String item) {
        insertItemToGroup(item, -1, -1);
    }

    /**
     * Adds an item to the an optgroup of the list box.
     *
     * @param item       the text of the item to be added
     * @param groupIndex the index of the optGroup where the item will be inserted
     */
    public void addItemToGroup(String item, int groupIndex) {
        insertItemToGroup(item, groupIndex, -1);
    }

    /**
     * Adds an item to the last optgroup of the list box.
     *
     * @param item the text of the item to be added
     */
    public void addItemToGroup(String item, String value) {
        insertItemToGroup(item, value, -1, -1);
    }

    /**
     * Adds an item to the an optgroup of the list box.
     *
     * @param item       the text of the item to be added
     * @param groupIndex the index of the optGroup where the item will be inserted
     */
    public void addItemToGroup(String item, String value, int groupIndex) {
        insertItemToGroup(item, value, groupIndex, -1);
    }

    public HandlerRegistration addMaxSelectedHandler(MaxSelectedHandler handler) {
        return ensureChosenHandlers().addHandler(MaxSelectedEvent.getType(),
                handler);
    }

    public HandlerRegistration addReadyHandler(ReadyHandler handler) {
        return ensureChosenHandlers().addHandler(ReadyEvent.getType(), handler);
    }

    public HandlerRegistration addShowingDropDownHandler(
            ShowingDropDownHandler handler) {
        return ensureChosenHandlers().addHandler(
                ShowingDropDownEvent.getType(), handler);
    }

    public HandlerRegistration addUpdatedHandler(UpdatedHandler handler) {
        return ensureChosenHandlers().addHandler(
                UpdatedEvent.getType(), handler);
    }

    @Override
    public void clear() {
        clear(true);
    }

    public void clear(boolean update) {
        $(getElement()).html("");
        if (update){
            update();
        }
    }

    @Override
    public void setEnabled(boolean enabled) {
        super.setEnabled(enabled);

        update();
    }

    public void forceRedraw() {
        $(getElement()).as(Chosen.Chosen).destroy()
                .chosen(options, ensureChosenHandlers());
    }

    public GQuery getChosenElement() {
        ChosenImpl impl = $(getElement()).data(Chosen.CHOSEN_DATA_KEY,
                ChosenImpl.class);
        if (impl != null) {
            return impl.getContainer();
        }
        return $();
    }

    public int getDisableSearchThreshold() {
        return options.getDisableSearchThreshold();
    }

    public int getMaxSelectedOptions() {
        return options.getMaxSelectedOptions();
    }

    public String getNoResultsText() {
        return options.getNoResultsText();
    }

    public String getPlaceholderText() {
        return options.getPlaceholderText();
    }

    public String getPlaceholderTextMultiple() {
        return options.getPlaceholderTextMultiple();
    }

    public String getPlaceholderTextSingle() {
        return options.getPlaceholderTextSingle();
    }

    /**
     * Return the value of the first selected option if any. Returns false otherwise.
     * In case of multiple ChosenListBox, please use {@link #getValues()} instead.
     * @return
     */
    public String getValue(){
        int selectedIndex = getSelectedIndex();

        return selectedIndex != -1 ? getValue(selectedIndex) : null;
    }

    /**
     * Return the values of all selected options in an array.
     * Usefull to know which options are selected in case of multiple ChosenListBox
     * @return
     */
    public String[] getValues() {
        if (!isMultipleSelect()){
            return new String[]{getValue()};
        }

        JsArrayString values = JsArrayString.createArray().cast();
        NodeList<OptionElement> options = SelectElement.as(getElement()).getOptions();
        for (int i = 0; i < options.getLength(); i++){
            OptionElement option = options.getItem(i);
            if (option.isSelected()){
                values.push(option.getValue());
            }
        }

        String[] result = new String[values.length()];
        for (int i = 0; i < values.length(); i++){
            result[i] = values.get(i);
        }

        return result;
    }

    /**
     * Insert a group to the list box.
     *
     * @param label the text of the group to be added
     * @param index the index at which to insert it
     */
    public void insertGroup(String label, int index) {
        insertGroup(label, null, index);
    }

    /**
     * Insert a group to the list box.
     *
     * @param label the text of the group to be added
     * @param id the id of the optgroup element
     * @param index the index at which to insert it
     */
    public void insertGroup(String label, String id, int index) {
        GQuery optGroup = $("<optgroup></optgroup>").attr("label", label);
        if (id != null){
            optGroup.attr("id", id);
        }
        GQuery select = $(getElement());

        int itemCount = SelectElement.as(getElement()).getLength();

        if (index < 0 || index > itemCount) {
            select.append(optGroup);
        } else {
            GQuery before = select.children().eq(index);
            before.before(optGroup);
        }
    }

    /**
     * Adds an item to the an optgroup of the list box. If no optgroup exists,
     * the item will be add at the end ot the list box.
     *
     * @param item       the text of the item to be added
     * @param value      the value of the item to be added
     * @param itemIndex  the index inside the optgroup at which to insert the item
     * @param groupIndex the index of the optGroup where the item will be inserted
     */
    public void insertItemToGroup(String item, Direction dir, String value,
            int groupIndex, int itemIndex) {
        GQuery optgroupList = $(OPTGROUP_TAG, getElement());

        int groupCount = optgroupList.size();

        if (groupCount == 0) {
            // simply insert the item to the listbox
            insertItem(item, dir, value, itemIndex);
            return;
        }

        if (groupIndex < 0 || groupIndex > groupCount - 1) {
            groupIndex = groupCount - 1;
        }

        GQuery optgroup = optgroupList.eq(groupIndex);

        OptionElement option = Document.get().createOptionElement();
        setOptionText(option, item, dir);
        option.setValue(value);

        int itemCount = optgroup.children().size();

        if (itemIndex < 0 || itemIndex > itemCount - 1) {
            optgroup.append(option);
        } else {
            GQuery before = optgroup.children().eq(itemIndex);
            before.before(option);
        }

    }

    /**
     * Adds an item to the an optgroup of the list box. If no optgroup exists,
     * the item will be add at the end ot the list box.
     *
     * @param item       the text of the item to be added
     * @param itemIndex  the index inside the optgroup at which to insert the item
     * @param groupIndex the index of the optGroup where the item will be inserted
     */

    public void insertItemToGroup(String item, int groupIndex, int itemIndex) {
        insertItemToGroup(item, null, item, groupIndex, itemIndex);

    }

    /**
     * Adds an item to the an optgroup of the list box. If no optgroup exists,
     * the item will be add at the end ot the list box.
     *
     * @param item       the text of the item to be added
     * @param value      the value of the item to be added
     * @param itemIndex  the index inside the optgroup at which to insert the item
     * @param groupIndex the index of the optGroup where the item will be inserted
     */
    public void insertItemToGroup(String item, String value, int groupIndex,
            int itemIndex) {
        insertItemToGroup(item, null, value, groupIndex, itemIndex);

    }

    /**
     * Specify if the deselection is allowed on single selects.
     */
    public boolean isAllowSingleDeselect() {
        return options.isAllowSingleDeselect();
    }

    public boolean isSearchContains() {
        return options.isSearchContains();
    }

    public boolean isSingleBackstrokeDelete() {
        return options.isSingleBackstrokeDelete();
    }

    public void removeGroup(int index){
        $(OPTGROUP_TAG, getElement()).eq(index).remove();
        update();
    }

    /**
     * Remove the optgroup (and the children options) by id.
     * To set an id to an optgroup, use {@link #insertGroup(String, String, int)} or {@link #addGroup(String, String)}
     * @param id
     */
    public void removeGroupById(String id){
        $("#"+id, getElement()).remove();
        update();
    }

    /**
     * Remove all optgroup (and the children options) with a label matching <code>label</code> argument
     * @param label
     */
    public void removeGroupByLabel(String label){
        $(OPTGROUP_TAG + "[label='" + label + "']", getElement()).remove();
        update();
    }

    public void setAllowSingleDeselect(boolean allowSingleDeselect) {
        options.setAllowSingleDeselect(allowSingleDeselect);
    }

    public void setDisableSearchThreshold(int disableSearchThreshold) {
        options.setDisableSearchThreshold(disableSearchThreshold);
    }
    
    public void setHideNoResult(boolean isHideNoResult) {
    	options.setHideNoResult(isHideNoResult);
    }
    
    public void setAddNewOptionVal(boolean isAddNewOptionVal) {
		options.setAddNewOptionVal(isAddNewOptionVal);
	}

    @Override
    public void setFocus(boolean focused) {
        GQuery focusElement = getFocusableElement();
        if (focused) {
            focusElement.focus();
        } else {
            focusElement.blur();
        }
    }

    public void setMaxSelectedOptions(int maxSelectedOptions) {
        options.setMaxSelectedOptions(maxSelectedOptions);
    }

    public void setNoResultsText(String noResultsText) {
        options.setNoResultsText(noResultsText);
    }

    public void setPlaceholderText(String placeholderText) {
        options.setPlaceholderText(placeholderText);
    }

    public void setPlaceholderTextMultiple(String placeholderTextMultiple) {
        options.setPlaceholderTextMultiple(placeholderTextMultiple);
    }

    public void setPlaceholderTextSingle(String placeholderTextSingle) {
        options.setPlaceholderTextSingle(placeholderTextSingle);
    }

    public void setSearchContains(boolean searchContains) {
        options.setSearchContains(searchContains);
    }

    @Override
    public void setSelectedIndex(int index) {
        super.setSelectedIndex(index);
        update();
    }

    public void setSingleBackstrokeDelete(boolean singleBackstrokeDelete) {
        options.setSingleBackstrokeDelete(singleBackstrokeDelete);
    }

    /**
     * Select all options with value present in <code>values</code> array and update the component.
     * @param values
     */
    public void setSelectedValue(String... values) {
        for (String value : values){
            Element element = $("option[value='" + value + "']", this).get(0);

            if (element != null) {
                OptionElement.as(element).setSelected(true);
            }
        }
        update();
    }

    @Override
    public void setVisible(boolean visible) {
        this.visible = visible;

        if (isSupported()) {
            GQuery chosenElement = getChosenElement();
            if (visible) {
                chosenElement.show();
            } else {
                chosenElement.hide();
            }
        } else {
            super.setVisible(visible);
        }
    }

    /**
     * Use this method to update the chosen list box (i.e. after insertion or
     * removal of options)
     */
    public void update() {
        ensureChosenHandlers().fireEvent(new UpdatedEvent());
    }

    protected final <H extends EventHandler> HandlerRegistration addChosenHandler(
            H handler, Type<H> type) {
        return ensureChosenHandlers().addHandler(type, handler);
    }

    protected EventBus ensureChosenHandlers() {
        return chznHandlerManager == null ? chznHandlerManager = new SimpleEventBus()
                : chznHandlerManager;
    }

    protected EventBus getChosenHandlerManager() {
        return chznHandlerManager;
    }
   

    @Override
    protected void onLoad() {
        super.onLoad();
        $(getElement()).as(Chosen.Chosen).chosen(options, ensureChosenHandlers());
        setVisible(visible);	
    }

    @Override
    protected void onUnload() {
        super.onUnload();
        $(getElement()).as(Chosen.Chosen).destroy();
    }

    private GQuery getFocusableElement() {
        GQuery chosen = getChosenElement();
        GQuery focusableElement = chosen.children("a");
        if (focusableElement.isEmpty()) {
            focusableElement = chosen.find("input");
        }
        return focusableElement;
    }

}
