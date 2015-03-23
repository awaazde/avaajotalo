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
package org.otalo.ao.client.util;

/**
 * @author nikhil
 *
 */
public class QueryParam {
	
	private String queryParam;
	private String queryValue;

	public QueryParam(String queryParam, String queryValue) {
		this.queryParam = queryParam;
		this.queryValue = queryValue;
	}
	
	/**
	 * @return the queryParam
	 */
	public String getQueryParam() {
		return queryParam;
	}
	/**
	 * @param queryParam the queryParam to set
	 */
	public void setQueryParam(String queryParam) {
		this.queryParam = queryParam;
	}
	/**
	 * @return the queryValue
	 */
	public String getQueryValue() {
		return queryValue;
	}
	/**
	 * @param queryValue the queryValue to set
	 */
	public void setQueryValue(String queryValue) {
		this.queryValue = queryValue;
	}
	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	@Override
	public String toString() {
		StringBuilder builder = new StringBuilder();
		builder.append("SearchQueryKeyVal [queryParam=");
		builder.append(queryParam);
		builder.append(", queryValue=");
		builder.append(queryValue);
		builder.append("]");
		return builder.toString();
	}
}