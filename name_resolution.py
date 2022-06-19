import os
from collections import defaultdict
import csv
from tqdm import tqdm
import json
import spacy
from spacy.matcher import PhraseMatcher
from multiprocessing import Pool
import re
import scispacy


nlp = spacy.load("en_core_sci_lg")


# extracts all plant names
with open("../Kew_Acc_Syn.csv", encoding="ISO-8859-1") as f:
    r = csv.DictReader(f)
    all_plants = [rr["taxon_name"].lower() for rr in tqdm(r)]

# store all multi-word plants (m) and all mult-word plants in a flattened list (flat_m),
#   and a precomputed list of plants that we know to be found as full names in the text (m2)
m = [p for p in all_plants if len(p.split()) > 1]
flat_m = list(set([mmm for mm in m for mmm in mm.split()]))
m2 = ['abelmoschus manihot', 'acacia mangium', 'acalypha multicaulis', 'acamptopappus sphaerocephalus', 'achillea biserrata', 'achillea millefolium', 'acokanthera oblongifolia', 'aconitum shennongjiaense', 'adenium obesum', 'aegilops caudata', 'aegilops comosa', 'aegilops crassa', 'aegilops cylindrica', 'aegilops geniculata', 'aegilops markgrafii', 'aegilops speltoides', 'aegilops squarrosa', 'aegilops tauschii', 'aegilops triuncialis', 'aegilops ventricosa', 'aegopodium tadshikorum', 'agrimonia eupatoria', 'agriophyllum lateriflorum', 'agropyron bessarabicum', 'agropyron cristatum', 'agropyron dasystachyum', 'agropyron desertorum', 'agropyron libanoticum', 'agropyron mongolicum', 'agropyron trachycaulum', 'agrostis canina', 'agrostis capillaris', 'allamanda blanchetii', 'allamanda cathartica', 'allamanda doniana', 'allamanda puberula', 'allamanda schottii', 'allium cepa', 'allium fistulosum', 'allium flavum', 'allium oleraceum', 'alstonia boonei', 'alstroemeria aurea', 'alstroemeria longistaminea', 'alternanthera paronychioides', 'alternanthera tenella', 'alyssoides utriculata', 'alyssum alyssoides', 'alyssum foliosum', 'alyssum fulvescens', 'amaranthus cruentus', 'amaranthus hypochondriacus', 'anabasis aphylla', 'anaphalis nepalensis', 'anemanthele lessoniana', 'anemone multifida', 'anemone xingyiensis', 'angelica komarovii', 'anthochlamys polygaloides', 'anthriscus glacialis', 'anthurium andraeanum', 'arabidopsis arenosa', 'arabidopsis lyrata', 'arabidopsis suecica', 'arabidopsis thaliana', 'arabis turczaninowii', 'arachis duranensis', 'arachis hypogaea', 'argemone mexicana', 'aristolochia birostris', 'artemisia adamsii', 'artemisia vulgaris', 'asclepias curassavica', 'aspidistra erecta', 'aspidistra obconica', 'aspidistra subrotata', 'aspidosperma pyrifolium', 'aster amellus', 'astraea lobata', 'astragalus frigidus', 'astragalus ladakensis', 'astragalus lasiophyllus', 'atriplex aucheri', 'atriplex canescens', 'atriplex leucoclada', 'atriplex micrantha', 'atriplex patens', 'atriplex tatarica', 'aulacospermum ikonnikovii', 'aulacospermum simplex', 'aulacospermum tianschanicum', 'australopyrum pectinatum', 'austrostipa stipoides', 'avena barbata', 'avena eriantha', 'avena fatua', 'avena maroccana', 'avena sativa', 'barbarea intermedia', 'barbarea orthoceras', 'bassia prostrata', 'bassia scoparia', 'begonia blancii', 'begonia guixiensis', 'begonia longgangensis', 'begonia moneta', 'begonia montaniformis', 'bellevalia mauritanica', 'bellevalia saviczii', 'berberis ceratophylla', 'beta vulgaris', 'bixa orellana', 'blitum virgatum', 'blutaparon vermiculare', 'boenninghausenia albiflora', 'bomarea edulis', 'boronia chartacea', 'boronia clavata', 'boronia pinnata', 'brachiaria brizantha', 'brachiaria ruziziensis', 'brachypodium distachyon', 'brachypodium hybridum', 'brachyscome dichromosomatica', 'brasenia schreberi', 'brassica alboglabra', 'brassica campestris', 'brassica carinata', 'brassica juncea', 'brassica maurorum', 'brassica napus', 'brassica nigra', 'brassica oleracea', 'brassica rapa', 'brickellia chenopodina', 'bromus cappadocicus', 'bromus inermis', 'bromus secalinus', 'bupleurum aitchisonii', 'burlemarxia pungens', 'calendula arvensis', 'callisia graminea', 'callisia monandra', 'callisia repens', 'callitriche obtusangula', 'caltha alba', 'caltha natans', 'caltha palustris', 'camellia assamica', 'camellia sinensis', 'campanula rotundifolia', 'campanumoea lancifolia', 'campanumoea parviflora', 'camphorosma lessingii', 'canna amabilis', 'cannabis sativa', 'capsella bursa', 'capsella bursa-pastoris', 'capsicum rhomboideum', 'cardamine amara', 'cardamine flexuosa', 'cardamine occulta', 'cardamine pratensis', 'cardamine rivularis', 'cardiospermum integerrimum', 'carex blepharicarpa', 'carex ciliatomarginata', 'carex cilicica', 'carex conica', 'carex pedunculata', 'carissa edulis', 'carissa macrocarpa', 'carlemannia tetragona', 'carthamus tinctorius', 'carya ovata', 'cecropia peltata', 'cenchrus ciliaris', 'centaurea jacea', 'centaurea stoebe', 'centratherum punctatum', 'cephalanthera longifolia', 'ceratozamia mexicana', 'chamerion angustifolium', 'chenopodium album', 'chenopodium pratericola', 'chenopodium probstii', 'chenopodium quinoa', 'chromolaena odorata', 'chrysolaena cognata', 'cicer arietinum', 'cicerbita lessertiana', 'cienfuegosia tripartita', 'cirsium altissimum', 'cirsium brevifolium', 'cirsium quercetorum', 'citrus assamensis', 'claytonia virginica', 'clematis graveolens', 'coffea arabica', 'coffea canephora', 'coix gigantea', 'colutea nepalensis', 'conyza canadensis', 'corallodiscus lanuginosus', 'coriandrum sativum', 'corydalis meifolia', 'crepis alpina', 'crepis balliana', 'crepis bursifolia', 'crepis capillaris', 'crepis incana', 'crepis sibthorpiana', 'crocus corsicus', 'crocus hyemalis', 'crocus sativus', 'croton argenteus', 'croton argyrophyllus', 'croton blanchetianus', 'croton glandulosus', 'croton heliotropiifolius', 'cryptocarya laevigata', 'ctenanthe burle-marxii', 'ctenanthe setosa', 'ctenium concinnum', 'cucumis hystrix', 'cucumis sativus', 'cucurbita pepo', 'cuminia eriantha', 'curcuma comosa', 'cyclamen persicum', 'cyclamen repandum', 'cymbopogon martini', 'cymodocea angustata', 'cynodon dactylon', 'dactylis glomerata', 'dactylorhiza majalis', 'dasypyrum breviaristatum', 'dasypyrum hordeaceum', 'dasypyrum villosum', 'daucus carota', 'deinacanthon urbanianum', 'delphinium roylei', 'delphinium uncinatum', 'deschampsia cespitosa', 'deyeuxia scabrescens', 'dianthus angulatus', 'dichorisandra hexandra', 'dioscorea alata', 'diospyros kaki', 'diplazium dilatatum', 'diplazium donianum', 'diplazium esculentum', 'diplazium hachijoense', 'diplazium mesosorum', 'diplazium wichurae', 'diplotaxis catholica', 'diplotaxis muralis', 'dorstenia mannii', 'dracocephalum thymiflorum', 'dypsis madagascariensis', 'echinochloa colonum', 'echinops graecus', 'eichhornia crassipes', 'elaeosticta bucharica', 'eleocharis geniculata', 'eleocharis maculosa', 'eleocharis montana', 'eleocharis ovata', 'eleocharis palustris', 'eleocharis sellowiana', 'eleocharis subarticulata', 'elephantopus mollis', 'eleutherine bulbosa', 'elwendia persica', 'elymus anthosachnoides', 'elymus canadensis', 'elymus confusus', 'elymus dolichatherus', 'elymus himalayanus', 'elymus magellanicus', 'elymus nutans', 'elymus panormitanus', 'elymus rectisetus', 'elymus repens', 'elymus shandongensis', 'elymus trachycaulus', 'elytrigia caespitosa', 'elytrigia repens', 'emilia sonchifolia', 'epidendrum cinnabarinum', 'epilobium angustifolium', 'epimedium koreanum', 'epimedium macranthum', 'eragrostis curvula', 'eranthemum capense', 'eremopyrum bonaepartis', 'erigeron alpinus', 'erigeron annuus', 'erigeron patentisquama', 'eryngium regnellii', 'erysimum hieraciifolium', 'eulaliopsis binata', 'evolvulus filipes', 'evolvulus glomeratus', 'fagopyrum esculentum', 'fagopyrum tataricum', 'fagus sylvatica', 'fallopia japonica', 'festuca arundinacea', 'festuca pratensis', 'festuca rubra', 'festulpia hubbardii', 'ficus carica', 'fragaria chiloensis', 'fragaria vesca', 'fragaria × ananassa', 'fraxinus americana', 'fritillaria japonica', 'fritillaria montana', 'fritillaria persica', 'fumaria indica', 'furcraea foetida', 'gagea pratensis', 'galitzkya macrocarpa', 'galium austriacum', 'gentiana aristata', 'gentiana pyrenaica', 'geranium lucidum', 'geranium pratense', 'gibasis geniculata', 'gibasis karwinskyana', 'gibasis rhodantha', 'gladiolus tenuis', 'glycine hirticaulis', 'glycine max', 'glycine tabacina', 'glycine tomentella', 'goeppertia ornata', 'gomortega nitida', 'gossypium arboreum', 'gossypium barbadense', 'gossypium herbaceum', 'gossypium hirsutum', 'grindelia camporum', 'gueldenstaedtia verna', 'gypsophila bermejoi', 'habranthus itaobinus', 'halodule pinifolia', 'hancornia speciosa', 'haplopappus gracilis', 'hedysarum argyrophyllum', 'hedysarum austrosibiricum', 'hedysarum cachemirianum', 'helianthus annuus', 'helianthus maximiliani', 'helictotrichon cincinnatum', 'heloniopsis orientalis', 'hemarthria compressa', 'hemiphylacus alatostylus', 'heracleum brunonis', 'heracleum dissectum', 'herissantia tiubae', 'heteranthera oblongifolia', 'hibiscus cannabinus', 'hieracium vulgatum', 'hierochloe australis', 'hippocrepis comosa', 'hordeum bogdanii', 'hordeum bulbosum', 'hordeum chilense', 'hordeum lechleri', 'hordeum marinum', 'hordeum murinum', 'hordeum parodii', 'hordeum pusillum', 'hordeum violaceum', 'hordeum vulgare', 'hylocereus monacanthus', 'hylocereus undatus', 'hymenoxys texana', 'hypericum elodeoides', 'hypericum perforatum', 'hystrix patula', 'illigera trifoliata', 'impatiens amphorata', 'impatiens reidii', 'indigofera hamiltonii', 'ipomoea longeramosa', 'ipomoea marcellia', 'iris boissieri', 'iris serotina', 'iris versicolor', 'iris xiphium', 'isatis indigotica', 'isoetes asiatica', 'isoetes japonica', 'isonema smeathmannii', 'ixeridium calcicola', 'ixeridium laevigatum', 'jacobaea vulgaris', 'jubaea chilensis', 'juncus biglumis', 'kengyilia laxiflora', 'kibara macrophylla', 'knautia maxima', 'kochia prostrata', 'kohautia platyphylla', 'landolphia membranacea', 'lathyrus ketzkhovelii', 'lathyrus odoratus', 'lathyrus palustris', 'lavatera olbia', 'lavatera trimestris', 'leontopodium alpinum', 'lepisorus angustus', 'lepisorus thunbergianus', 'lesquerella fendleri', 'lessingianthus laniferus', 'lessingianthus niederleinii', 'leucaena confertiflora', 'leymus mollis', 'lilium longiflorum', 'limodorum abortivum', 'limonium sinuatum', 'linum usitatissimum', 'lippia alba', 'livistona chinensis', 'lolium multiflorum', 'lolium perenne', 'lomatocarpa albomarginata', 'lotus corniculatus', 'lupinus polyphyllus', 'luzula elegans', 'luzula multiflora', 'lycium ferocissimum', 'lycopus maackianus', 'lycopus uniflorus', 'lycoris aurea', 'magadania victoris', 'maihuenia patagonica', 'mandevilla sancta', 'mandevilla tenuifolia', 'maranta arundinacea', 'marantochloa conferta', 'marica gracilis', 'marsdenia altissima', 'marsdenia caatingae', 'matelea ganglinosa', 'mecardonia flagellaris', 'medicago lesinsii', 'medicago murex', 'medicago sativa', 'medicago truncatula', 'megaphrynium macrostachyum', 'melandrium album', 'mentha arvensis', 'merremia aegyptia', 'micranthes foliolosa', 'miersia chilensis', 'mikania sericea', 'milium effusum', 'milium montianum', 'minuartia anatolica', 'minuartia corymbulosa', 'miscanthus purpurascens', 'miscanthus sacchariflorus', 'monochoria vaginalis', 'moricandia arvensis', 'musa acuminata', 'musa ingens', 'musa textilis', 'narcissus dubius', 'narcissus × alentejanus', 'nasturtium officinale', 'neomarica northiana', 'nicotiana glauca', 'nicotiana paniculata', 'nicotiana rustica', 'nicotiana sylvestris', 'nicotiana tabacum', 'odontadenia hypoglauca', 'odontarrhena obovata', 'oenothera pycnocarpa', 'olneya tesota', 'ophelia chinensis', 'ophioglossum petiolatum', 'orchis morio', 'ornithogalum narbonense', 'ornithogalum umbellatum', 'orthophytum amoenum', 'orychophragmus violaceus', 'oryza eichingeri', 'oryza punctata', 'oryza rufipogon', 'oryza sativa', 'oryzopsis hymenoides', 'oxalis corymbosa', 'oxytropis chankaensis', 'pachycereus pringlei', 'pachyphytum fittkaui', 'paeonia tenuifolia', 'panicum virgatum', 'papaver bracteatum', 'papaver persicum', 'papaver rhoeas', 'paralychnophora reflexoauriculata', 'parthenium argentatum', 'paspalum almum', 'paspalum dilatatum', 'paspalum malmeanum', 'paspalum rufum', 'paspalum urvillei', 'pastinaca sativa', 'pelargonium incarnatum', 'peltastes peltatus', 'pennisetum americanum', 'pennisetum orientale', 'pennisetum purpureum', 'pereskia aculeata', 'petrosimonia brachiata', 'petunia integrifolia', 'petunia parodii', 'phaseolus leptostachyus', 'phaseolus macvaughii', 'phaseolus vulgaris', 'philodendron pedatum', 'phleum nodosum', 'phleum pratense', 'phlox drummondii', 'phrynium terminale', 'phyllospadix iwatensis', 'picea glauca', 'pilosocereus aureispinus', 'pilosocereus aurisetus', 'pinguicula lusitanica', 'piptatherum racemosum', 'pisum sativum', 'plantago lagopus', 'plantago media', 'plantago ovata', 'plantago patagonica', 'platycodon grandiflorus', 'pleurospermum uralense', 'poa shumushuensis', 'poa sibirica', 'poa sinaica', 'poa skvortzovii', 'poa stepposa', 'poa sublanata', 'poa sylvicola', 'poa tatewakiana', 'poa trivialis', 'poa turneri', 'poa urssulensis', 'polyalthia fragrans', 'polyalthia humbertii', 'polypogon monspeliensis', 'potamogeton crispus', 'potentilla argentea', 'potentilla atrosanguinea', 'potentilla sundaica', 'potentilla thomsonii', 'primula egaliksensis', 'prospero autumnale', 'prunus avium', 'prunus cerasus', 'prunus virginiana', 'psathyrostachys huashanica', 'psathyrostachys juncea', 'pseudoroegneria libanotica', 'pseudoroegneria spicata', 'pseudoroegneria stipifolia', 'pseudoroegneria strigosa', 'psygmorchis pusilla', 'pteris cretica', 'pteris grevilleana', 'puccinellia distans', 'puccinellia kurilensis', 'ranunculus adoneus', 'ranunculus cantoniensis', 'ranunculus codyanus', 'ranunculus diffusus', 'ranunculus pedatus', 'raphanus sativus', 'rauvolfia vomitoria', 'rhynchospora tenuis', 'roegneria ciliaris', 'rostraria cristata', 'rubus parvifolius', 'rumex acetosa', 'rumex papillaris', 'rytidosperma thomsonii', 'saccharum officinarum', 'saccharum robustum', 'saccharum spontaneum', 'sacoila argentina', 'salix suchowensis', 'salvia pratensis', 'salvinia natans', 'saruma henryi', 'saxifraga filicaulis', 'saxifraga virginiensis', 'scabiosa olivieri', 'scaevola taccada', 'schizozygia coffeoides', 'schulzia prostrata', 'scilla autumnalis', 'scilla cyrenaica', 'scilla scilloides', 'scorzonera taurica', 'scutellaria baicalensis', 'secale cereale', 'sedum suaveolens', 'senecio cambrensis', 'senecio nikoensis', 'senecio squalidus', 'senecio vulgaris', 'sequoia sempervirens', 'seseli indicum', 'sesleria caerulea', 'sesleria uliginosa', 'setaria barbata', 'setaria glauca', 'silene conoidea', 'silene latifolia', 'sinapis alba', 'sinosenecio albonervius', 'sinosenecio baojingensis', 'sinosenecio chienii', 'sinosenecio homogyniphyllus', 'sinosenecio hupingshanensis', 'sinosenecio jiangxiensis', 'sinosenecio nanchuanicus', 'sisymbrium austriacum', 'sisymbrium strictum', 'sisyrinchium filifolium', 'solanum acaule', 'solanum brevicaule', 'solanum brevidens', 'solanum bulbocastanum', 'solanum chacoense', 'solanum commersonii', 'solanum demissum', 'solanum lycopersicum', 'solanum melongena', 'solanum scabrum', 'solanum stoloniferum', 'solanum tuberosum', 'solanum verrucosum', 'solanum × rechei', 'sonchus tenerrimus', 'sorghum bicolor', 'sorghum grande', 'sorghum halepense', 'sparattanthelium amazonum', 'spartina alterniflora', 'spartina anglica', 'spartina foliosa', 'spinacia oleracea', 'stellaria graminea', 'stellaria media', 'stellaria monosperma', 'stellaria semivestita', 'stemmadenia galeottiana', 'stemodia hyptoides', 'stipa californica', 'stipecoma peltigera', 'strasburgeria robusta', 'streptocarpus beampingaratrensis', 'suaeda maritima', 'symphytum officinale', 'synotis xinningensis', 'tagetes jaliscensis', 'tagetes patula', 'taraxacum stevenii', 'thalia geniculata', 'thalictrum foetidum', 'thalictrum foliolosum', 'thermopsis alpina', 'thinopyrum bessarabicum', 'thinopyrum elongatum', 'thinopyrum intermedium', 'thinopyrum junceiforme', 'thinopyrum junceum', 'thinopyrum ponticum', 'thymus loscosii', 'tordyliopsis brunonis', 'trachystoma ballii', 'tradescantia ambigua', 'tradescantia paludosa', 'tragopogon orientalis', 'trifolium pratense', 'trifolium repens', 'trifolium subterraneum', 'trigonella brachycarpa', 'trigonella coerulescens', 'trigonella corniculata', 'trigonella procumbens', 'trigonobalanus verticillata', 'tripleurospermum subpolare', 'tripsacum dactyloides', 'trisetum flavescens', 'triticum aegilopoides', 'triticum aestivum', 'triticum boeoticum', 'triticum crassum', 'triticum dicoccoides', 'triticum durum', 'triticum monococcum', 'triticum syriacum', 'triticum tauschii', 'triticum timopheevii', 'triticum turgidum', 'triticum urartu', 'triumfetta pilosa', 'turanecio eriospermus', 'turanecio pandurifolius', 'turnera sidoides', 'typhonium jinpingense', 'urospermum picroides', 'valeriana jatamansi', 'valeriana officinalis', 'vella pseudocytisus', 'vellozia glabra', 'vellozia variegata', 'vicia cracca', 'vicia faba', 'victoria amazonica', 'vinca rosea', 'viola betonicifolia', 'viola canescens', 'viola collina', 'viola tricolor', 'vitis vinifera', 'zea diploperennis', 'zea mays', 'zea perennis', 'zephyranthes brachyandra', 'zephyranthes robusta', 'zephyranthes rosea', 'zephyranthes sylvatica', 'zingeria biebersteiniana', 'zingeria trichopoda', 'zostera marina']

# potentially_added_plants: all plants found in the filtered docs (precomputed)
#   out of those store the single-words that are parts of any multi-word plant - so we can treat them as aliases
with open("./potentially_added_plants.txt") as f:
    ls = f.readlines()
pot = [line.strip().lower() for line in ls]
pot_s_partial = set(pot).intersection(set(flat_m))

# mapping from single word to multi-word plant name, first (d2 dict) for each part of the multi-words,
#   and then (d dict) only for those who actually appear in the filtered docs
d2 = defaultdict(list)
for mm in m:
    for mmm in mm.split():
        d2[mmm].append(mm)

d = defaultdict(list)
for p in pot_s_partial:
    d[p] = d2[p]


# this function extracts the textual data from the filtered doc so it could be consumed by spacy model
def get_docs():
    with open("filtered_docs.jsonl", encoding="ISO-8859-1") as ff:
        ls2 = ff.readlines()
    for i, l in enumerate(ls2):
        li = json.loads(l)
        doc = ""
        if 'title' in li and li['title']:
            doc += li['title']
        if 'abstract' in li and li['abstract']:
            doc += (" " if doc.endswith(".") else " . ") + li['abstract']
        if 's2orc' in li and li['s2orc'] and 'pdf_parse' in li['s2orc'] and li['s2orc']['pdf_parse']:
            if 'body_text' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['body_text']:
                for sec in li['s2orc']['pdf_parse']['body_text']:
                    if 'text' in sec and sec['text']:
                        doc += (" " if doc.endswith(".") else " . ") + sec['text']
            if 'ref_entries' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['ref_entries']:
                for ref in li['s2orc']['pdf_parse']['ref_entries'].values():
                    if 'text' in ref and ref['text']:
                        doc += (" " if doc.endswith(".") else " . ") + ref['text']
        yield {"doc_text": doc, "doc_url": li['extra']['s2_url']}


docs = list(get_docs())


# create spacy matchers for the single words (matcher) and multi words (matcher2)
patterns = [nlp.make_doc(text) for text in pot_s_partial]
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher.add("TerminologyList", patterns)
patterns2 = [nlp.make_doc(text) for text in m2]
matcher2 = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher2.add("TerminologyList2", patterns2)


def get_cc_span(sent, info):
    cc_start = -1
    cc_end = -1
    for ind, w in enumerate(sent[:-1]):
        if w.idx - sent[0].idx <= info.start() <= sent[ind + 1].idx - 1 - sent[0].idx:
            cc_start = w.i - sent[0].i
        elif w.idx - sent[0].idx <= info.end() <= sent[ind + 1].idx - 1 - sent[0].idx:
            cc_end = w.i - sent[0].i
            break

    return cc_start, cc_end


# worker function: per each sent in the given doc, check
def manipulate_doc(doc_details):
    doc = doc_details["doc_url"]
    doc_text = doc_details["doc_text"]
    ret = {"heuristic_a_1": defaultdict(list), "heuristic_a_n": defaultdict(list), "heuristic_b_1": defaultdict(list), "heuristic_b_n": defaultdict(list), "heuristic_b_0": defaultdict(list)}
    if len(doc_text) > 999999:
        print(f"doc: {doc} too long: {len(doc_text)}")
        return []
    try:
        spacy_doc = nlp(doc_text)
    except:
        print(f"doc: {doc} exception")
        return []
    doc_lowered = doc_text.lower()
    csv_out = []
    for sent in spacy_doc.sents:
        if ("2n=" in sent.text) or ("2n =" in sent.text):
            matches = list(matcher(sent))
            for _, from_, to_ in matches:
                plant = spacy_doc[from_:to_].text.lower()
                plant_start = from_ - sent[0].i
                plant_end = to_ - sent[0].i - 1
                # check that no full name of the current alias name already appears in the sentence
                #   because it will be matched in the full name matcher
                if len([full_name for full_name in d[plant] if full_name in sent.text.lower()]) == 0:
                    full_name_matches = set([full_name for full_name in d[plant] if full_name in doc_lowered])
                    if len(full_name_matches) == 1:
                        ret["heuristic_a_1"][(plant, doc)].append({"full_name_matches": full_name_matches, "sent_text": sent.text})
                        all_ccs = list(zip(list(re.finditer("2n.*?=\s*([0-9]+)[^a-zA-Z+]", sent.text)), re.findall("2n.*?=\s*([0-9]+)[^a-zA-Z+]", sent.text)))
                        for (info, cc) in all_ccs:
                            cc_start, cc_end = get_cc_span(sent, info)
                            dis, reversed_order = (plant_start - cc_end, 1) if (plant_start - cc_end > 0) else (cc_start - plant_end, 0)
                            csv_out.append({"plant": list(full_name_matches)[0], "CC": cc, "s2_url": doc, "sentence": sent.text, "priority": (1, len(matches), len(all_ccs), dis, reversed_order)})
                    elif len(full_name_matches) > 1:
                        ret["heuristic_a_n"][(plant, doc)].append({"full_name_matches": full_name_matches, "sent_text": sent.text})
                    else:
                        full_name_matches2 = set([full_name for full_name in d[plant]
                                                  if all(word in doc_lowered.split() for word in full_name.split())])
                        if len(full_name_matches2) == 1:
                            ret["heuristic_b_1"][(plant, doc)].append({"full_name_matches": full_name_matches2, "sent_text": sent.text})
                            all_ccs = list(zip(list(re.finditer("2n.*?=\s*([0-9]+)[^a-zA-Z+]", sent.text)), re.findall("2n.*?=\s*([0-9]+)[^a-zA-Z+]", sent.text)))
                            for (info, cc) in all_ccs:
                                cc_start, cc_end = get_cc_span(sent, info)
                                dis, reversed_order = (plant_start - cc_end, 1) if (plant_start - cc_end > 0) else (cc_start - plant_end, 0)
                                csv_out.append({"plant": list(full_name_matches2)[0], "CC": cc, "s2_url": doc, "sentence": sent.text, "priority": (2, len(matches), len(all_ccs), dis, reversed_order)})
                        elif len(full_name_matches2) > 1:
                            ret["heuristic_b_n"][(plant, doc)].append({"full_name_matches": full_name_matches2, "sent_text": sent.text})
                        else:
                            ret["heuristic_b_0"][(plant, doc)].append({"full_name_matches": [], "sent_text": sent.text})
            matches = list(matcher2(sent))
            for _, from_, to_ in matches:
                plant = spacy_doc[from_:to_].text.lower()
                all_ccs = list(zip(list(re.finditer("2n.*?=\s*([0-9]+)[^a-zA-Z+]", sent.text)), re.findall("2n.*?=\s*([0-9]+)[^a-zA-Z+]", sent.text)))
                plant_start = from_ - sent[0].i
                plant_end = to_ - sent[0].i - 1
                for (info, cc) in all_ccs:
                    cc_start, cc_end = get_cc_span(sent, info)
                    dis, reversed_order = (plant_start - cc_end, 1) if (plant_start - cc_end > 0) else (cc_start - plant_end, 0)
                    csv_out.append({"plant": plant, "CC": cc, "s2_url": doc, "sentence": sent.text, "priority": (0, len(matches), len(all_ccs), dis, reversed_order)})
    return ret, csv_out


# run multi-threaded and aggregate results
final_csv = []
final_ret = {"heuristic_a_1": defaultdict(list), "heuristic_a_n": defaultdict(list), "heuristic_b_1": defaultdict(list), "heuristic_b_n": defaultdict(list), "heuristic_b_0": defaultdict(list)}

with Pool(16) as p:
    for w, c in p.map(manipulate_doc, docs):
        final_ret["heuristic_a_1"].update(w["heuristic_a_1"])
        final_ret["heuristic_a_n"].update(w["heuristic_a_n"])
        final_ret["heuristic_b_1"].update(w["heuristic_b_1"])
        final_ret["heuristic_b_n"].update(w["heuristic_b_n"])
        final_ret["heuristic_b_0"].update(w["heuristic_b_0"])
        final_csv.extend(c)


# output results to full_names.csv
if os.path.exists("full_names.csv"):
    with open("full_names.csv") as f:
        data = f.read()
    with open("prev/full_names.csv", "w") as f:
        f.write(data)

fieldnames = ["plant", "CC", "s2_url", "sentence", "priority"]
with open('full_names.csv', 'w', encoding='utf8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_csv)


# print and store examples and statistics
print(f'heuristic_a_1: {len(final_ret["heuristic_a_1"])}, heuristic_a_n: {len(final_ret["heuristic_a_n"])}, heuristic_b_1: {len(final_ret["heuristic_b_1"])}, heuristic_b_n: {len(final_ret["heuristic_b_n"])}, heuristic_b_0: {len(final_ret["heuristic_b_0"])}')
# heuristic_a_1: 3197, heuristic_a_n: 249, heuristic_b_1: 2203, heuristic_b_n: 1629, heuristic_b_0: 17645

print(f'heuristic_a_1 unique plants: {len(set([list(pp["full_name_matches"])[0] for p in final_ret["heuristic_a_1"].values() for pp in p]))}, heuristic_b_1 unique plants: {len(set([list(pp["full_name_matches"])[0] for p in final_ret["heuristic_b_1"].values() for pp in p]))}')
# heuristic_a_1 unique plants: 1745, heuristic_b_1 unique plants: 1503

print(f'heuristic_a_1 unique partial plants: {len(set([p[0] for p in final_ret["heuristic_a_1"].keys()]))}, '
      f'heuristic_a_n unique partial plants: {len(set([p[0] for p in final_ret["heuristic_a_n"].keys()]))}, '
      f'heuristic_b_1 unique partial plants: {len(set([p[0] for p in final_ret["heuristic_b_1"].keys()]))}, '
      f'heuristic_b_n unique partial plants: {len(set([p[0] for p in final_ret["heuristic_b_n"].keys()]))}, '
      f'heuristic_b_0 unique partial plants: {len(set([p[0] for p in final_ret["heuristic_b_0"].keys()]))}')
# heuristic_a_1 unique partial plants: 1341, heuristic_a_n unique partial plants: 169, heuristic_b_1 unique partial plants: 1224, heuristic_b_n unique partial plants: 803
# , heuristic_b_0 unique partial plants: 3709

if os.path.exists("prev/full_names_heuristics_examples.json"):
    with open("prev/full_names_heuristics_examples.json") as f:
        data = f.read()
    with open("prev/full_names_heuristics_examples.json", "w") as f:
        f.write(data)

with open("prev/full_names_heuristics_examples.json", "w") as f3:
    for k, v in final_ret.items():
        f3.write(f"\n\nExamples for {k}:\n")
        for kk, vv in sorted([xx for xx in v.items()], key=lambda xxx: len(xxx[0][1]))[:25]:
            try:
                f3.write(f'{kk}, {vv}' + "\n")
            except:
                pass

# Reading the statistics file and parsing it
#
# with open("full_names_heuristics_examples.json", encoding="ISO-8859-1") as f:
#     ls3 = f.readlines()
#
# partials_counts = defaultdict(list)
# full_name_counts = defaultdict(list)
# which = {0: "heuristic_a_1", 1: "heuristic_a_n", 2: "heuristic_b_1", 3: "heuristic_b_n", 4: "heuristic_b_0"}
# i = 0
# for j, l in enumerate(ls3):
#     asd = l.split(" [{'full_name_matches': ")
#     if len(asd) < 2:
#         continue
#     partial = asd[0].split("', ")[0][2:]
#     fns_pre_split = asd[1].split("'}, 'sent_text':")[0]
#     if fns_pre_split[0] == '[':
#         fns = []
#     else:
#         fns = fns_pre_split[2:].split("', '")
#     if (len(fns) > 1 and i in [0, 2]) or (len(fns) == 1 and i == 1) or (len(fns) == 0 and i == 3):
#         i += 1
#     partials_counts[which[i]].append(partial)
#     full_name_counts[which[i]].extend(fns)
#
