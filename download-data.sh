#cd /workspace/datasets

# Check if `kaggle` command exists
if ! command -v kaggle &> /dev/null; then
    echo "'kaggle' command does not exist. Please install it first."
    exit 1
fi
echo "Downloading Kaggle"
kaggle competitions download -c acm-sf-chapter-hackathon-big
unzip acm-sf-chapter-hackathon-big.zip
tar -xf product_data.tar.gz
echo "Cleaning up to save space:"
rm acm-sf-chapter-hackathon-big.zip
rm product_data.tar.gz
rm popular_skus.csv