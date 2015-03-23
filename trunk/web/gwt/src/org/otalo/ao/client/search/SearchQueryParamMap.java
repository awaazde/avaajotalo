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

import java.util.ArrayList;

import org.otalo.ao.client.util.QueryParam;

/**
 * @author nikhil
 *
 */
public class SearchQueryParamMap extends ArrayList<QueryParam> {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	@Override
	public boolean add(QueryParam queryParam) {
		if(this.contains(queryParam))
			this.remove(queryParam.getQueryParam());
		else { //first iterating through list and removing older version of it
			if(this.size()>0) {
				for(int count=0;count<this.size();count++) {
					if(queryParam.getQueryParam().equalsIgnoreCase(((QueryParam) this.get(count)).getQueryParam())) {
						this.remove(count);
						break;
					}
				}
			}
		}
		//now adding it into list
		return super.add(queryParam);
	}

	@Override
	public void add(int index, QueryParam queryParam) {
		this.add(queryParam);
	}

	public boolean remove(String queryParam) {
		for(int count=0;count<this.size();count++) {
			if(((QueryParam)this.get(count)).getQueryParam().equalsIgnoreCase(queryParam)) {
				this.remove(this.get(count));
				return true;
			}
		}
		return false;
	}

	/**
	 * Returns json string for all of the values
	 * @return the json string
	 */
	public String jsonString() {
		StringBuilder builder = new StringBuilder();
		boolean first = true;
		builder.append('{');
		for (QueryParam queryParam: this) {
			if (!first) {
				builder.append(',');
			} else {
				first = false;
			}
			write(queryParam.getQueryParam(), builder);
			builder.append(':');
			write(queryParam.getQueryValue(), builder);
		}
		
		builder.append('}');
		return builder.toString();
	}

	/**
	 * toString representation for the custom string builder.
	 * returns list of comma seperator values
	 */
	@Override
	public String toString() {
		StringBuilder selectedValues = new StringBuilder();
		if(this.size() > 0) {
			for(int count=0;count<this.size();count++) {
				selectedValues.append(this.get(count)).append(",");
			}
		}
		selectedValues.deleteCharAt(selectedValues.length()-1);

		return selectedValues.toString();
	}

	/**
	 * Appends the data into string builder
	 * @param data
	 * @param writer
	 */
	private void write(String data, StringBuilder builder) {
		if (data == null) {
			builder.append("null");
			return;
		}

		builder.append('"');
		for (int i = 0, n = data.length(); i < n; ++i) {
			final char c = data.charAt(i);
			switch (c) {
			case '\\':
			case '"':
				builder.append('\\').append(c);
				break;
			case '\b':
				builder.append("\\b");
				break;
			case '\t':
				builder.append("\\t");
				break;
			case '\n':
				builder.append("\\n");
				break;
			case '\f':
				builder.append("\\f");
				break;
			case '\r':
				builder.append("\\r");
				break;
			default:
				builder.append(c);
			}
		}
		builder.append('"');
	}
}
