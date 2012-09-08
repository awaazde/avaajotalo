/*
 * Copyright 2010 Google Inc.
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
import java.util.Set;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.Membership;
import org.otalo.ao.client.model.Membership.MembershipStatus;

import com.google.gwt.view.client.HasData;
import com.google.gwt.view.client.ListDataProvider;
import com.google.gwt.view.client.ProvidesKey;

/**
 * The data source for contact information used in the sample.
 */
public class MemberDatabase {

  /**
   * Information about a member.
   */
  public static class MemberInfo implements Comparable<MemberInfo> {

    /**
     * The key provider that provides the unique ID of a contact.
     */
    public static final ProvidesKey<MemberInfo> KEY_PROVIDER = new ProvidesKey<MemberInfo>() {
      public Object getKey(MemberInfo item) {
        return item == null ? null : item.getId();
      }
    };
      
    private Membership membership;

    public MemberInfo(Membership membership) {
    	this.membership = membership;
    }

    public int compareTo(MemberInfo o) {
      return (o == null || o.getName() == null) ? -1
          : -o.getName().compareTo(getName());
    }

    @Override
    public boolean equals(Object o) {
      if (o instanceof MemberInfo) {
        return getId() == ((MemberInfo) o).getId();
      }
      return false;
    }

    /**
     * @return the status of the membership
     */
    public MembershipStatus getStatus() {
      return membership.getStatus();
    }

    /**
     * @return the unique ID of the member
     */
    public String getId() {
      return membership.getId();
    }

    /**
     * @return the contact's name
     */
    public String getName() {
    	String name = membership.getMemberName();
    	if ("null".equals(name))
    		return "";
    	else
    		return name; 
    }

    /**
     * @return the contact's number
     */
    public String getNumber() {
      return membership.getUser().getNumber();
    }
    
    /**
     * Set the member's name.
     *
     */
    public void setName(String name) {
    	// check if name changed
    	if (!getName().equals(name) && !name.equals(""))
    	{
    		String data = "name=" + name;
        JSONRequest.doPost(AoAPI.UPDATE_MEMBER + getId() + "/", data);
    	}
      
    }
    
    /**
     * Set the member's number.
     *
     */
    public void setNumber(String number) {
    	if (!getNumber().equals(number) && !number.equals(""))
    	{
	      String data = "number=" + number;
	      JSONRequest.doPost(AoAPI.UPDATE_MEMBER + getId() + "/", data);
    	}
    }

    /**
     * Set the member's membership.
     *
     * @param category the category to set
     */
    public void setMembership(Membership membership) {
      assert membership != null : "membership cannot be null";
      this.membership = membership;
    }
  }
  
  
  /**
   * The singleton instance of the database.
   */
  private static MemberDatabase instance;
  private List<MemberInfo> members = new ArrayList<MemberInfo>(), joinRequests = new ArrayList<MemberInfo>();
  

  /**
   * Get the singleton instance of the contact database.
   *
   * @return the singleton instance
   */
  public static MemberDatabase get() {
    if (instance == null) {
      instance = new MemberDatabase();
    }
    return instance;
  }

  /**
   * The provider that holds the list of contacts in the database.
   */
  private ListDataProvider<MemberInfo> dataProvider = new ListDataProvider<MemberInfo>();

  /**
   * Construct a new contact database.
   */
  private MemberDatabase() {

  }

  /**
   * Add list of members. We are doing this in a slightly non-clean
   * way to avoid two seperate server hits for members that display on
   * Members and those that display as Join Requests. The server will
   * return back both together, we sort them out here. We then define
   * separate methods for displaying either for any tables that are connected.
   * Note that this only works if the tables are not in view at the same time,
   * since both tables will be populated with the same data on either
   * method's invocation.
   *
   * @param newmembers the members to add.
   */
  public void addMembers(List<Membership> newmembers) {
  	this.members.clear();
  	this.joinRequests.clear();
    
    for (Membership m : newmembers)
    {
    	if (m.getStatus() == MembershipStatus.REQUESTED)
    		joinRequests.add(new MemberInfo(m));
    	else
    		members.add(new MemberInfo(m));
    }
    
  }
  
  /**
   * This only works if the tables are not in view at the same time,
   * since both (all) tables will be populated with the same data on either
   * method's invocation.
   */
  public void displayMembers()
  {
  	List<MemberInfo> members = dataProvider.getList();
    members.clear();
    
    for (MemberInfo m : this.members)
    {
    	members.add(m);
    }
    
    refreshDisplays();
  }
  
  /**
   * This only works if the tables are not in view at the same time,
   * since both (all) tables will be populated with the same data on either
   * method's invocation.
   */
  public void displayJoinRequests()
  {
  	List<MemberInfo> members = dataProvider.getList();
    members.clear();
    for (MemberInfo m : this.joinRequests)
    {
    	members.add(m);
    }
    
    refreshDisplays();
  }

  public void filterBy(MembershipStatus status)
  {
  	List<MemberInfo> members = dataProvider.getList();
  	members.clear();
  	for (MemberInfo m : this.members)
    {
  		if (status == null || m.getStatus() == status)
  			members.add(m);
    }
  	
  	refreshDisplays();
  }
  /**
   * Add a display to the database. The current range of interest of the display
   * will be populated with data.
   *
   * @param display a {@Link HasData}.
   */
  public void addDataDisplay(HasData<MemberInfo> display) {
    dataProvider.addDataDisplay(display);
  }


  public ListDataProvider<MemberInfo> getDataProvider() {
    return dataProvider;
  }

  /**
   * Refresh all displays.
   */
  public void refreshDisplays() {
    for (HasData<MemberInfo> d : dataProvider.getDataDisplays())
    {
    	d.setRowCount(members.size());
    	for (MemberInfo m : members)
    	{
    		d.getSelectionModel().setSelected(m, false);
    	}
    	for (MemberInfo m : joinRequests)
    	{
    		d.getSelectionModel().setSelected(m, false);
    	}
    }
    dataProvider.refresh();
  }

}
