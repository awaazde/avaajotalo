package org.otalo.ao.client.model;

public class User extends BaseModel {
	public User(JSOModel data) {
		super(data);
	}

	public String getNumber()
	{
		return getObject("fields").get("number");
	}
	
	public String getName()
	{
		return getObject("fields").get("name");
	}
	
	public String getDistrict()
	{
		return getObject("fields").get("district");
	}
	
	public String getTaluka()
	{
		return getObject("fields").get("taluka");
	}
	
	public String getVillage()
	{
		return getObject("fields").get("village");
	}
	
}
