from harvester.metadata import MetadataFormat
from harvester.oaipmh.metadata import global_metadata_registry, oai_dc_reader


class OAI_DC(MetadataFormat):
    
    header = ('OAI_IDENTIFIER', 
              'DC_TITLE',
              'DC_CREATOR',
              'DC_SUBJECT',
              'DC_DESCRIPTION',
              'DC_PUBLISHER',
              'DC_CONTRIBUTOR',
              'DC_DATE',
              'DC_TYPE',
              'DC_FORMAT',
              'DC_IDENTIFIER',
              'DC_SOURCE',
              'DC_LANGUAGE',
              'DC_RELATION',
              'DC_COVERAGE',
              'DC_RIGHTS')
    
    def process_record(self, identifier, metadata):

        metadata_map = metadata.getMap()
        data = {}
        data["oai_identifier"] = identifier
        data["title"] = metadata_map.get('title',[])
        data["creator"] = metadata_map.get('creator',[])
        data["subject"] = metadata_map.get('subject',[])
        data["description"] = metadata_map.get('description',[])
        data["publisher"] = metadata_map.get('publisher',[])
        data["contributor"] = metadata_map.get('contributor',[])
        data["date"] = metadata_map.get('date',[])
        data["type"] = metadata_map.get('type',[])
        data["format"] = metadata_map.get('format',[])
        data["identifier"] = metadata_map.get('identifier',[])
        data["source"] = metadata_map.get('source',[])
        data["language"] = metadata_map.get('language',[])
        data["relation"] = metadata_map.get('relation',[])
        data["coverage"] = metadata_map.get('coverage',[])
        data["rights"] = metadata_map.get('rights',[])

        return (
            data["oai_identifier"],
            u"|".join(data["title"]).encode('utf-8'),
            u"|".join(data["creator"]).encode('utf-8'),
            u"|".join(data["subject"]).encode('utf-8'),
            u"|".join(data["description"]).encode('utf-8'),
            u"|".join(data["publisher"]).encode('utf-8'),
            u"|".join(data["contributor"]).encode('utf-8'),
            u"|".join(data["date"]).encode('utf-8'),
            u"|".join(data["type"]).encode('utf-8'),
            u"|".join(data["format"]).encode('utf-8'),
            u"|".join(data["identifier"]).encode('utf-8'),
            u"|".join(data["source"]).encode('utf-8'),
            u"|".join(data["language"]).encode('utf-8'),
            u"|".join(data["relation"]).encode('utf-8'),
            u"|".join(data["coverage"]).encode('utf-8'),
            u"|".join(data["rights"]).encode('utf-8')
        )


global_metadata_registry.registerReader('oai_dc', oai_dc_reader)    
