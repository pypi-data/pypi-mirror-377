# Selection API Discussion
- [1. Overview](#1-Overview)
	- [1.1. Design Principles](#11-design-principles)
	- [1.2. Feature Requirements](#12-feature-requirements)
	- [1.3. Example Use Cases](#13-example-use-cases)
- [2. ipyaladin interfaces](#2-ipyaladin-interfaces)
	- [2.1. GET](#21-get)
	- [2.2. SELECT](#22-select)
- [3. aladin-lite interfaces](#3-aladin-lite-interfaces)
	- [3.1. Listeners](#31-Listeners)
	- [3.2. GET](#32-get)
	- [3.3. SELECT](#33-select)
	- [3.4. Misc](#34-misc)
- [4. Discussion Topics](#4-discussion-topics)
# 1. Overview

To enable analysis of data from the Roman telescope, we are building out tools for the cloud-based Roman Research Nexus platform. We are developing a suite of interoperable tools within a JupyterLab environment, and are integrating **aladin-lite** into this toolset through **ipyaladin**.

To support user workflows, we need to expose **aladin-lite**'s features programmatically. Our initial focus is on selection functionality, which is foundational for many use cases.

We examined the current selection features available in **ipyaladin** and **aladin-lite**, and prototyped an API to support:
- selecting a list of sources ([PR](https://github.com/pcuste1/ipyaladin/pull/2))
- selecting sources within a region
	- aladin-lite([PR](https://github.com/pcuste1/aladin-lite/pull/1))
	- ipyaladin ([PR](https://github.com/pcuste1/ipyaladin/pull/3))

These proofs-of-concept work by implementing the API discussed below. We also examined footprint selection, which will require further discussion to determine the best path forward. 
## 1.1. Design Principles
#### Standard Interface Pattern
For each feature exposed by **aladin-lite** and **ipyaladin** that we intend to support, the interface should offer the following APIs:
- **Listener**: Allows developers to attach callbacks to respond to relevant events.
- **Get**: Retrieves the current state or value of the feature.
- **Set (Select)**: Updates the feature\'s state programmatically. 
- **Misc:** Features that support the other 3.

This pattern ensures clarity, predictability, and ease of use across all supported functionality.
#### Separation of Concerns
It is essential to clearly distinguish between the roles of the **ipyaladin** and **aladin-lite** APIs. While many capabilities in **ipyaladin** serve as direct proxies for **aladin-lite** features, this is not always the case. **ipyaladin** is a higher-level interface that may combine multiple **aladin-lite** operations to deliver more integrated or complex functionality. Furthermore, the timing of releases, versioning, and updates can lead to separation of functionality and efforts.

For example, although **aladin-lite** may expose individual APIs for selecting catalog objects and footprints, **ipyaladin** might provide a unified API that coordinates both actions under a single interface call.
#### Consistent Data Formats
To streamline development and enhance user experience, all **ipyaladin** interfaces are expected to rely on **Astropy** object formats (e.g., [Table](https://docs.astropy.org/en/stable/table/index.html), [Region](https://astropy-regions.readthedocs.io/en/stable/)). This provides a familiar and well-documented foundation for users working within the scientific Python ecosystem.
#### User-Defined Catalogs
All selection interfaces are designed with the assumption that catalogs are loaded into **aladin-lite** programmatically by the user within their Jupyter notebook. Catalogs added directly via the widget interface are not considered within the scope of these APIs, ensuring greater control and consistency for programmatic workflows.
#### Layer Agnostic APIs
In the initial implementation, we make the assumption that all APIs will operate across all the currently visible layers loaded by the user in the UI. This approach mirrors the existing functionality of **aladin-lite** through the existing `GetSelection` method. 
## 1.2. Feature Requirements
#### Selection Requirements
As a notebook user/scientist I want to\...
- select a source within a catalog using a programmatic API
- select a list of sources within all loaded catalogs using a programmatic API
- select a footprint(s) using a programmatic API 
- select all sources/footprints within a defined region using a programmatic API
#### Data Retrieval Requirements 
As a notebook user/scientist I want to\...
- access the list of currently selected sources using a programmatic API 
- access the list of currently select footprints currently selected using a programmatic API 
- access the region used to select the sources/footprints using a programmatic API 
#### Listener Requirements 
As a developer, I want to\...
- listen for changes to the selected source(s) 
- listen for changes to the selection region
- listen for changes to the selected footprint(s)
#### Misc. Requirements
As a notebook user/scientist I want to\...
- be able to remove the current selection(s) using a programmatic API

## 1.3. Example Use Cases
**Use case 1:** A scientist is interested in all sources in a catalog with a redshift within a defined range. The query might look like the following:

```
aladin.selectSources(match_func: lambda source: source.rshift > 1 and source.rshift < 2)
```

**Use case 2:** A scientist is interested in a subset of sources in a catalog. Since they loaded the catalog themselves, they know that there is an `objId`  field that uniquely identifies the source. The query might look like the following: 

```
aladin.selectSources(sources=catalog_subset, match_key="objId")
```

If they instead want to use `RA` and `DEC` to identify the source, the query might look like the following:

```
aladin.selectSources(sources=catalog_subset, match_keys=["ra", "dec"])
```

**Use case 3:** A software engineer wants to create an interoperable layer between **ipyaladin** and another visualization tool, such as [jdaviz](https://jdaviz.readthedocs.io/en/stable/). They would then need to use a combination of the APIs listed in this doc to ensure that selections in **ipyaladin** are reflected in **jdaviz** and vice versa. 

# 2. ipyaladin interfaces
## 2.1. GET
#### get_selection

```
def get_selection() -> List[Table]
```

Returns a list of **Astropy** `Table` containing the currently selected catalog source(s) per catalog.
#### get_region

```
def get_region() -> Region
```

Returns an **Astropy** `Region` with the currently selected region (if applicable)
#### get_footprints

```
def get_footprints() -> List[Footprint]
```

Returns a list of the currently selected footprint(s)
## 2.2. SELECT
#### select_sources
A few alternatives are provided for the selection functionality, and each has potential use cases and should be considered. 
##### Option 1:

```
def select_sources(selection: Table, match_keys: List[Str]) -> None
```

Send a request to **aladin-lite** to select sources defined in an **Astropy** `Table`. The keys provided in `match_key` are used to match the sources with corresponding entries in the catalogs.

| **Parameter** | **Type**                                                     | **Description**                                                                                                     |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| selection     | [Table](https://docs.astropy.org/en/stable/table/index.html) | Table of sources to select                                                                                          |
| match_keys    | List[Str]                                                    | Keys within the table to use to match a source in the selection table to the sources loaded in aladin-lite catalogs |

------------------------------------------------------------------------------------------------------------------------------------
##### Option 2:

```
def select_sources(selection: Table, match_key: Str) -> None
```

Send a request to **aladin-lite** to select sources defined in an **Astropy** `Table`. The key provided in `match_key` are used to match the sources with corresponding entries in the catalogs. This could be implemented as a convenience method that calls Option 1.

| **Parameter** | **Type**                                                     | **Description**                                                                                                    |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| selection     | [Table](https://docs.astropy.org/en/stable/table/index.html) | Table of sources to select                                                                                         |
| match_key     | Str                                                          | Key within the table to use to match a source in the selection table to the sources loaded in aladin-lite catalogs |

---------------------------------------------------------------------------------------------------------------------------------------
##### Option 3:

```
def select_sources(match_func: Callable) -> None
```

Sends a request to **aladin-lite** to select all sources that match the provided function.

**Parameter** |**Type** |**Description**
--------------- |---------- |-----------------------------------------------------
match_func |lambda |Lambda expression that defines matching criteria for sources

--------------------------------------------------------------------------------
#### select_region

```
def select_region(region: Region) -> None
```

This method triggers a selection by `Region` event based on the coordinates 

**Parameter** |**Type** |**Description**
--------------- |---------------------------------------------------------------------------------------------------| -------------------------------------------------------
region |[Region](https://astropy-regions.readthedocs.io/en/stable/api/regions.Region.html#regions.Region) |The region corresponding to the sky coordinates that the user would like to select sources within

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#### select_footprints

```
def select_footprints(footprints: List[Footprint]) -> None
```

This method triggers a selection event on a user provided list of Foorprints

| **Parameter** | **Type**        | **Description**                                      |
| ------------- | --------------- | ---------------------------------------------------- |
| footprints    | List[Footprint] | The list of footprints the user would like to select |

-------------------------------------------------------------------------
# 3. aladin-lite interfaces
## 3.1. Listeners
Supported listeners that enable us to attach callback functions to events that occur within **aladin-lite**.

**Event Name** |**Description** |**Data** |**Supported**
------------------ |---------------------------- |------------------- |---------------
objectsSelected |Fired when objects are selected by region, represents the individual objects selected |List of sources |Existing
regionsSelected |Fired when objects are selected by region, represents the region used to select the objects |Shape of the region selected|Proposed
objectClicked |Fires when an object is clicked | Catalog object(s) and xy coordinates of the click event | Existing
footprintClicked |Fires when a footprint is clicked | Footprint object(s) xy coordinates of the click event | Existing

-----------------------------------------------------------------------------------
## 3.2. GET
#### GetSelectedSources

```
/**
* @returns List[Sources]
*/
function GetSelectedSources()
```

Returns the list of currently selected source objects.
#### GetSelectedRegion

```
/**
* @returns Region
*/
function GetSelectedRegion()
```

Returns the region definition of the selection event, if a `Region` was used to select. This would require updates to **aladin-lite** to maintain knowledge of the regions used to select, which is not currently done explicitly, but can be accessed through the [selector Finite State Machines](https://github.com/cds-astro/aladin-lite/tree/master/src/js/FiniteStateMachine). 
#### GetSelectedFootprints

```
/**
*@returns List[Footprint]
*/
function GetSelectedFootprints()
```

Returns the currently selected `List[Footprint]`
## 3.3. SELECT
#### SelectSources 
##### Option 1: 

```
/**
* @param sources: List[Source]
* @param match_keys: List[str]
*/
function SelectSources(sources, match_keys)
```

Selects the list of sources provided by the user within **aladin-lite**. The list of keys provided in `match_keys` are used to match the sources with corresponding entries in the catalogs.

| **Parameter** | **Type**     | **Description**                              |
| ------------- | ------------ | -------------------------------------------- |
| sources       | List[Source] | The list of sources to select.               |
| match_keys    | List[str]    | The list of keys to use to determine a match |

-----------------------------------------------------------------------------
##### Option 2:

```
/**
* @param match_func: func()
*/
function SelectSources(match_func)
```

Selects the list of sources provided. Uses the `match_func` provided to determine if a source should be selected. This is similar to how region selections are currently performed in **aladin-lite**, where a function [s.contains( ... )](https://github.com/cds-astro/aladin-lite/blob/master/src/js/FiniteStateMachine/CircleSelect.js#L85-L102) is defined. 

| **Parameter** | **Type**  | **Description**                                                |
| ------------- | --------- | -------------------------------------------------------------- |
| match_func    | func(a,b) | The function used to determine if an object should be selected |

-------------------------------------------------------------------------------
#### SelectRegion

```
/**
* @param region: Region
*/
function SelectRegion(region)
```

Triggers a `Region` selection within **aladin-lite** widget. This function would need to mock of the various state transitions expected by the FiniteStateMachines used for region selection ([example](https://github.com/cds-astro/aladin-lite/blob/master/src/js/FiniteStateMachine/CircleSelect.js#L137-L165)).

| **Parameter** | **Type** | **Description**                     |
| ------------- | -------- | ----------------------------------- |
| region        | Region   | The region to select objects within |

-----------------------------------------------------------------------
#### SelectFootprints

```
/**
* @param footprints: List[Footprint]
*/
function SelectFootprints(footprints)
```

Triggers a `Footprint` selection within **aladin-lite** widget

| **Parameter** | **Type**        | **Description**                  |
| ------------- | --------------- | -------------------------------- |
| footprints    | List[Footprint] | The list of footprints to select |
## 3.4. Misc
#### RemoveSelection

```
function RemoveSelection()
```

Removes the current selection from **aladin-lite** widget. This would effectively be a passthrough for the `view.unselectObjects()` method.

# 4. Discussion Topics
## 4.1 Spatial Regions vs. Regions in Screen Coordinates
A key challenge identified is the mismatch between how regions are represented in **aladin-lite** and **Astropy**. In **aladin-lite**, regions are defined as connected points on a celestial sphere, while **Astropy** represents them as shapes on a 2D image plane. At small angular resolutions, the discrepancies are minimal, but as the region size increases, the inaccuracies become more pronounced.

From a discussion on the **Astropy** GitHub ([link](https://github.com/astropy/regions/issues/564))
> Sky regions are regions that are defined using celestial coordinates. Please note they are not defined as regions on the celestial sphere, but rather are meant to represent shapes on an image. They simply use sky coordinates instead of pixel coordinates to define their position. The remaining shape parameters are converted to pixels using the pixel scale of the image.

Our demo implementation addresses one of these discrepancies by treating rectangles as polygons. This is necessary because **Astropy** represents rectangles using a center point, width, and height, while **aladin-lite** defines them as four distinct vertices.
##### Questions for CDS
- Are there recommended approaches for reconciling celestial sphere regions with 2D image plane representations in **Astropy**?
- Beyond **Astropy** regions, are there other libraries or data structures that can better handle the translation between celestial and image coordinates?
- Should we implement a warning system to inform users when regions exceed a specified angular resolution, indicating potential inaccuracies?
- Would there be any benefit to storing the regions as MOCs?
## 4.2 Path Forward
If the approach outlined above is accepted, we are ready to submit draft pull requests for review. These drafts will implement the APIs discussed in this document, and we are prepared to make any necessary revisions based on the feedback we receive from CDS.

Looking ahead, we anticipate further significant updates to the API. To enable a smoother development and review process, we would like the schedule more frequent touch points to help align our goals.
##### Questions for CDS
- What next steps do you see moving forward with this suggestion?
- What collaboration tools do you prefer?
## 4.3 Footprint Selection
**Identifying Footprints**:
Are there any best practices for uniquely identifying a footprint for selection? This may argue for the potential catalog storage of footprints with columns and key pairs that uniquely identify them. 

**Footprints as catalog elements:**
Currently when a "catalog" is loaded and it has an `s_region` column, the footprints defined by that column are rendered in Aladin Lite. Seeing this in action led to the questions:
- Should handling of footprints and catalog sources could be more unified?
- Is any unification like that already planned?

For example, footprint selection could fire the same event(s) as object selection, and could result in displaying the metadata in a table or popup as with catalog object selection. The catalog columns could also help in differentiating footprints when needed.

**Region-Based Footprint Selection:**
When performing a region selection, are footprints considered selected only if they are entirely contained within the region, or are footprints that overlap with the region also included? Clarifying this behavior will be important for us moving forward as we implement consistent selection logic across multiple tools.

**Skewer Selection:**
We are also exploring the feasibility of a skewer selection feature. This functionality would allow users to select all footprints that intersect with a given point. Is this type of selection currently supported, or would it require new API functionality?
## 4.4 Future Items
In the future, we may want to consider implementing a version of the UI that operates on individual catalogs. We may also want to implement a UI method for toggling the visibility of a catalog.