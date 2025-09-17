# Histomic Atlases of Variation Of Cancers (HAVOC)

HAVOC is a versatile tool that maps histomic heterogeneity across H&E-stained digital slide images to help guide regional deployment of molecular resources to the most relevant/biodiverse tumor niches

## Cloud usage
Explore HAVOC on https://www.codido.co to run on the cloud

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install havoc-clustering.

!! Tensorflow will need to be installed as well as OpenSlide (https://openslide.org/download/) !!

```bash
pip install havoc-clustering
```

## Usage


```python
from havoc_clustering.havoc import HAVOC
from havoc_clustering.general_utility.slide import Slide

# create a new Slide object that represents the image.
# Requirements allow to filter out undesired images within ie a loop
s = Slide(
    slide_path,
    img_requirements={
        'compression': [70],
        'mpp': None  # all mpp values (magnification) are supported currently
    }
)

# to instantiate a HAVOC instance requires the following:
# 1. a Slide object
# 2. path to a tensorflow model which acts as the feature extractor to base clustering off of. 
    # Our model used in our works can be found at https://bitbucket.org/diamandislabii/faust-feature-vectors-2019/src/master/models/74_class/
# 3. the directory to save output to
# 4. size of the tiles to extract and work with within the slide. default is 1024 (original trained size for the model above)
# 5. by default, we use the slide's resized thumbnail as the background for the colortile map. turn off to make it HD at the expense of time
havoc = HAVOC(s, feature_extractor_path, save_dir, tile_size=512, hd_backdrop=False)

# to run, requires the following:
# 1. the k values to use for clustering
# 2. the blank filter cutoff. 0.5 means that there must be less than (100-50=50)% blank within a tile to decide to use it.
    # ie tiles that are >50% blank would be skipped; a non-conservative number to only cluster tiles with plentiful tissue
# 3. the layer name within the feature extractor model that is responsible for generating the features
# 4. Additional kwargs; OPTIONAL
kwargs = {
    # saves a thumbnail image of the original slide
    'save_thumbnail': False,
    # make a dendrogram of the clustering used to make the colortile maps (generated for each k value)
    'make_dendrogram': True,
    # make a tsne of each color cluster (generated for each k value)
    'make_tsne': True,
    # make a Pearson coeffcient clustermap of each color cluster (generated for each k value)
    'make_corr_map': True,
    # save the tiles belonging to each color cluster within the colortile map for a given k
    # ie [4,9] would save the colored tiles belonging to k=4 and k=9
    # NOTE: this should be a subset of k_vals
    'save_tiles_k_vals': []
}
havoc.run(k_vals=[9], min_non_blank_amt=0.5, layer_name='global_average_pooling2d_1', **kwargs)
```

## Result output
- Colortiled maps
- CSV file of cluster info + DLFVs (cluster_info_df.csv)
- Optionally:
    - Original slide thumbnail
    - TSNEs
    - Dendrograms
    - Correlation clustermap

## Multi-slide correlation map

By running HAVOC on multiple slides, you may want to combine all the generated correlation clustermaps into a mega clustermap.

1. Create a folder containing each slide's cluster_info_df.csv file
2. 
```python
from havoc_clustering.correlation_of_dlfv_groups import create_correlation_clustermap_multi_slide

create_correlation_clustermap_multi_slide(folder_of_csvs, target_k=9)
```

NOTE: the target_k should be a k-value you ran HAVOC with 

## Citation

Please refer to the paper "HAVOC: Small-scale histomic mapping of biodiversity across entire tumor specimens using deep neural networks"

## License
[GNU General Public License v3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.txt)
