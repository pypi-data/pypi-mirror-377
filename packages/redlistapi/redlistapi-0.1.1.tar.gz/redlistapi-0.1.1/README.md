# redlistapi

## IUCN Red List API python interface

## Description
A python interface and library for the IUCN Red List API [https://api.iucnredlist.org/](https://api.iucnredlist.org/)

## Installation

### Non-spatial
    pip install redlistapi

### Spatial

The Python GDAL library requires system-level libraries. Install GDAL headers before using:

Ubuntu/Debian:

    # first install the OS GDAL binaries
    # then install the python GDAL version that matches your OS binaries
    sudo apt install libgdal-dev
    pip install gdal==`gdal-config --version`

macOS (Homebrew): **untested

    brew install gdal

Windows: **untested

    Use precompiled wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/

Then install the package with spatial dependencies:

    pip install redlistapi[spatial]


## Usage
To use this library you must first obtain a personal [IUCN Red List API token](https://api.iucnredlist.org/).

The library has 3 main use approaches:


### Direct API endpoints
For direct endpoints the return value is the raw API response to allow parsing pages.

Openapi endpoints fall in 3 categories.
 
``` 
File-like endpoints  
  Note there is no trailing "/".  
  e.g.: api/v4/information/api_version
 
Folder-like endpoints
    Note there is a trailing "/".
    e.g.: api/v4/taxa/kingdom/
 
Parametrized endpoints
    Note there can be several file-like endpoints.
    e.g.: api/v4/taxa/kingdom/{kingdom_name}
```

#### File-like endpoints
    redlistapi.api.v4.information.api_version(token=token).json()
    redlistapi.api.v4.information.red_list_version(token=token).json()

#### Folder-like and Parametrized endpoints split in `list` and `by_` endpoints
    redlistapi.api.v4.taxa.family.list(token=token).json()
    redlistapi.api.v4.taxa.kingdom.list(token=token).json()
    redlistapi.api.v4.taxa.kingdom.by_kingdom_name(token=token, kingdom_name='CHROMISTA', year_published='2023').json()

### Simplified user-end interface
The simplified user-end interface simply eliminates the need to enter the token.  
This is useful for interactive use.

    interface = redlistapi.V4_Interface(token)  
    interface.information.api_version().json()  
    animalia = interface.taxa.kingdom.by_kingdom_name(kingdom_name='animalia')  
    animalia

### Assessment Class and Factory
The Assessment Factory is a class that returns Assessment Classes.

The Assessment Class exposes exposes all data available from a Red List Assessment.

    assessment_factory = redlistapi.AssessmentFactory(token=token)  
      
    upupa = assessment_factory.from_assessment_id(assessment_id=181836360)  
    upupa = assessment_factory.from_scientific_name(genus_name='Upupa', species_name='epops')  
    upupa = assessment_factory.from_taxid(taxid=22682655)  
      
    help(upupa)  
    upupa.assessment_as_pandas()

## Support
Submit requests and bugs on the repository's git page (https://gitlab.com/daniele.baisero/redlistapi).  
Or contact Daniele Baisero (daniele.baisero-at-gmail.com).

## Contributing
Contribution and collaboration offers are always welcome!

## Authors and acknowledgment
Daniele Baisero, 2025.

## License
MIT license; read LICENSE file.

## Project status
Ongoing development.
