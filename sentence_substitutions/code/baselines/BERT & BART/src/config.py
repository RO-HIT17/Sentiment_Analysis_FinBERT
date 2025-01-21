import os, time

import transformers
transformers.logging.set_verbosity(50)

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--train_data_choice", type=str, default='wiki_ppdb_lexical_s')


class Config(object):

    # model and expriment name -------------------------------------------------
    # ( change to expreiment with different settings ) -------------------------

    # # choose a model backbone
    model_choice = 'mlm_cls' # bert
    # model_choice = 'seq2seq' # bart

    loss_alpha_rej_alpha = 0.05 # in mlm_cls, loss = \alpha * {the words that keet unchanged} + {the words that is substituted}

    if 'mlm' in model_choice:
        plm_type = 'bert'
    elif 'seq2seq' in model_choice:
        plm_type = 'bart'

    # # decide the output dir
    exp_id = '1'

    # training arguments -------------------------------------------------------

    gpuid = '0'

    batch_size = 32 if 'mlm' not in model_choice else 64
    test_batch_size = 1

    num_epochs = 15
    save_epoch = 1
    lr = 0.0007
    warmup = 0
    gamma = 0.8
    max_norm = 1e-5 # Clipped gradient norm
    gradient_acc_steps = 1 # No. of steps of gradient accumulation
    hidden_dropout_prob = 0.1
    seed = 0

    train = 1 # do train or not
    infer = 1 # do infer or not

    train_use = 2000 # use [:train_use] data for train
    save_model = 1
    print_log = 1
    use_reverse_wiki = 1 if train else 0

    # file directories ---------------------------------------------------------
    # ( Don't need to change unless needed, i.e. PLM model paths ) -------------

    bert_path = 'bert-base-uncased'
    bart_path = 'facebook/bart-base'

    data_path = '../../../../data/sws_ds/sws_ds.json'
    data_path = '/home/v-chenswang/iven/code/WriteModelTraining/WordSubstitution/data/wiki/wiki_170_s-lexical-1-1014.json'
    dev_data_path = '../../../../data/sws/sws_eval.json'
    test_data_path = '../../../../data/sws/sws_test.json'

    # PLM atrtributes ----------------------------------------------------------
    # ( Don't need to change unless the world is destroyed ) -------------------

    if plm_type == 'bert':
        unk_id = 100
        mask_token = '[MASK]'
        cls_token = '[CLS]'
        sep_token = '[SEP]'
        mask_id = 103
        pad_id = 0
    elif plm_type == 'bart':
        unk_id = 3
        mask_token = '<mask>'
        cls_token = '<s>'
        sep_token = '</s>'
        mask_id = 50264
        pad_id = 1

    # FIXED file directories ---------------------------------------------------
    # ( Don't need to change unless the world is destroyed ) -------------------

    #output_root = '../output/'
    #os.makedirs(output_root, exist_ok=True)
    #exp_paths = os.path.join(output_root, exp_id)
    #nowtime = time.strftime('%m%d-%H:%M')

    # Output directory root
    output_root = '../output/'

    # Experiment ID and model choice
    exp_id = '1'
    model_choice = 'mlm_cls'

    # Replace invalid characters in timestamp (e.g., ":" in Windows)
    nowtime = time.strftime('%m%d-%H%M')

    # Construct the directory paths properly
    exp_paths = os.path.join(output_root, exp_id)
    os.makedirs(exp_paths, exist_ok=True)

    # Update `exp_id` and define the output path
    exp_id = os.path.join(exp_id, model_choice)
    output_path = os.path.join(output_root, exp_id)
    os.makedirs(output_path, exist_ok=True)

    # Checkpoint directory
    ckpt_path = os.path.join(output_path, 'ckpt/')
    os.makedirs(ckpt_path, exist_ok=True)

    # Append timestamp to the output path
    output_path = os.path.join(output_path, nowtime)
    os.makedirs(output_path, exist_ok=True)

    # Define additional paths
    log_path = os.path.join(output_path, 'log.log')
    res_path = os.path.join(output_path, 'eval')
    os.makedirs(res_path, exist_ok=True)

    # Paths for saving models
    best_model_path = os.path.join(output_path, "best.pth.tar")
    last_model_path = os.path.join(output_path, "last.pth.tar")

    # Debugging logs
    print(f"Experiment Paths Created: {exp_paths}")
    print(f"Output Path: {output_path}")
    print(f"Checkpoint Path: {ckpt_path}")
    print(f"Log File Path: {log_path}")
    print(f"Results Path: {res_path}")