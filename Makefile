PREPARE=./prepare-food-microbiome.py
SPLIT=/projet/maiage/save/textemig/projet-work/software/misc-utils/split.py
ALVISNLP=/projet/maiage/save/textemig/projet-work/software/install/alvisnlp/bin/alvisnlp

PUBMED=predictions/PubMed_lives-in.txt
GENBANK=predictions/genbank_mappings.txt
DSMZ=predictions/dsmz-taxon-habitat-mappings.txt
CIRM=predictions/CIRM_08022018.txt

BACTERIA_TAXAID=resources/taxa+id_Bacteria.txt

HABITAT_FOCUS=etc/habitat-focus.txt

BIOSAMPLE_ALL=resources/biosample_set.xml
BACTERIA_IDS=resources/bacteria-ids.txt

default:
	@echo output/food-microbiome-habitats : habitat prediction tables
	@echo resources/biosample-split : BioSample filtered \(bacteria\) and split
	@echo output/biosample-attributes-count.txt : usage of BioSample Attributes
	@echo output/biosample-table.txt : summary table of BioSample

output/food-microbiome-habitats: $(PREPARE) $(BACTERIA_TAXAID) $(HABITAT_FOCUS) $(PUBMED) $(GENBANK) $(DSMZ) $(CIRM)
	mkdir -p $@
	./$^

resources/bacteria-ids.txt: $(BACTERIA_TAXAID)
	cut -f 2 $< | uniq >$@

resources/biosample-split: $(BIOSAMPLE_ALL) $(BACTERIA_IDS)
	mkdir -p $@
	$(SPLIT) --begin '<BioSample ' --end '</BioSample>' --header '<?xml version="1.0" encoding="UTF-8"?>\n<BioSampleSet>\n' --footer '</BioSampleSet>\n' --dictionary $(BACTERIA_IDS) -n 10000 --filter '<Organism taxonomy_id="(\d+)"' --pattern '$@/biosample-%06d.xml' $<

output/biosample-attributes-count.txt: resources/biosample-split
	grep -Pho 'harmonized_name="[^"]*"' $</*.xml | sed -e 's,",,g' -e 's,harmonized_name=,,' | sort | uniq -c | sort -n >$@

output/biosample-table.txt: biosample.plan resources/biosample-split
	$(ALVISNLP) -log alvisnlp.log -verbose $<

clean:
	$(RM) -r $(TARGET)
