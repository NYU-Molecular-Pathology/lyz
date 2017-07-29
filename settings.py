# simple settings file that is source'd/imported by both Python and bash
# values MUST be in the format of key="value"
# use full paths only

script_dir="/ifs/data/molecpathlab/scripts"
nextseq_dir="/ifs/data/molecpathlab/quicksilver"
NGS580_analysis_dir="/ifs/data/molecpathlab/NGS580_WES"
bin_dir="/ifs/data/molecpathlab/bin"

auto_demultiplex_dir="/ifs/data/molecpathlab/quicksilver/to_be_demultiplexed"
auto_demultiplex_log_dir="/ifs/data/molecpathlab/quicksilver/automatic_demultiplexing_logs"

NGS580_auto_demultiplex_dir="/ifs/data/molecpathlab/quicksilver/to_be_demultiplexed/NGS580"
Archer_auto_demultiplex_dir="/ifs/data/molecpathlab/quicksilver/to_be_demultiplexed/Archer"

email_recipients_file="/ifs/data/molecpathlab/scripts/email_recipients.txt"
demultiplexing_email_recipients_file="/ifs/data/molecpathlab/scripts/email_recipients.txt"

demultiplex_NGS580_WES_script="/ifs/data/molecpathlab/scripts/demultiplexing/demultiplex-NGS580-WES.sh"
demultiplex_archer_script="/ifs/data/molecpathlab/scripts/demultiplexing/demultiplex-archer.sh"
bcl2fastq_217_script="/ifs/data/molecpathlab/scripts/demultiplexing/bcl2fastq.217.sh"

demultiplexing_postprocessing_script="/ifs/data/molecpathlab/scripts/demultiplexing/post_processing.sh"

NextSeq_index_file="/ifs/data/molecpathlab/quicksilver/run_index/NextSeq_run_index.csv"
NextSeq_sample_index_file="/ifs/data/molecpathlab/quicksilver/run_index/NextSeq_sample_index.csv"

sequencer_index_script="/ifs/data/molecpathlab/scripts/misc/sequencer_index.py"
sequencer_xml_parse_script="/ifs/data/molecpathlab/scripts/misc/parse_run_params_xml.py"


generate_demultiplexing_reports="/ifs/data/molecpathlab/scripts/generate-demultiplexing-reports/create_reports.py"


# mail_demultiplexing_results_script="/ifs/data/molecpathlab/scripts/demultiplexing/mail_demultiplexing_results.sh"

mail_demultiplexing_results_script="/ifs/data/molecpathlab/scripts/demultiplexing/mail_demultiplexing_results.py"

demultiplexing_stats_repo="/ifs/data/molecpathlab/scripts/demultiplexing-stats"

activate_miniconda="/ifs/data/molecpathlab/scripts/bin_scripts/activate_miniconda.sh"

# ssh key authentication needs to be set up for all users on these servers
email_server_address_file="/ifs/data/molecpathlab/private_data/server.txt"
default_localhost_address_file="/ifs/data/molecpathlab/private_data/server.txt"

# contains some of the same items as above, but meant for use only in Python:
sequencer_settings_file="/ifs/data/molecpathlab/scripts/run-monitor/sequencer_settings.json"
