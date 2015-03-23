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

import java.util.ArrayList;

/**
 * @author nikhil
 *
 */
public class CustomStringBuilder extends ArrayList<String> {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

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
		if(selectedValues.length()>1)
			selectedValues.deleteCharAt(selectedValues.length()-1);
		return selectedValues.toString();
	}
}
