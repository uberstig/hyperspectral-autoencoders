'''
    File name: autoencoder_train_MLP_advanced.py
    Author: Lloyd Windrim
    Date created: August 2019
    Python package: deephyp

    Description: An example script for training several different models for a given MLP (or dense) autoencoder
    architecture using the Pavia Uni hyperspectral dataset. Each model is trained with a different loss function.

'''


import scipy.io
import urllib
import os
import shutil
from utils import reporthook


# import toolbox libraries
import sys
sys.path.insert(0, '..')
from deephyp import autoencoder
from deephyp import data


if __name__ == '__main__':

    # download dataset (if already downloaded, comment this out)
    #urllib.urlretrieve( 'http://www.ehu.eus/ccwintco/uploads/e/ee/PaviaU.mat', os.path.join(os.getcwd(),'PaviaU.mat'), reporthook )

    # read data into numpy array
    mat = scipy.io.loadmat( 'PaviaU.mat' )
    img = mat[ 'paviaU' ]

    # create a hyperspectral dataset object from the numpy array
    hypData = data.HypImg( img )

    # pre-process data to make the model easier to train
    hypData.pre_process( 'minmax' )

    # create data iterator objects for training and validation using the pre-processed data
    trainSamples = 200000
    valSamples = 100
    dataTrain = data.Iterator( dataSamples=hypData.spectraPrep[:trainSamples, :],
                              targets=hypData.spectraPrep[:trainSamples, :], batchSize=1000 )
    dataVal = data.Iterator( dataSamples=hypData.spectraPrep[trainSamples:trainSamples+valSamples, :],
                            targets=hypData.spectraPrep[trainSamples:trainSamples+valSamples, :] )

    # shuffle training data
    dataTrain.shuffle()

    # setup a fully-connected autoencoder neural network with 3 encoder layers
    net = autoencoder.mlp_1D_network( inputSize=hypData.numBands, encoderSize=[50,30,10,3], activationFunc='relu',
                                      weightInitOpt='truncated_normal', tiedWeights=None, skipConnect=False )

    # setup multiple training operations for the network (with different loss functions)
    net.add_train_op(name='sse', lossFunc='SSE', learning_rate=1e-3, decay_steps=None, decay_rate=None,
                     method='Adam', wd_lambda=0.0)

    net.add_train_op( name='csa', lossFunc='CSA', learning_rate=1e-3, decay_steps=None, decay_rate=None,
                      method='Adam', wd_lambda=0.0 )

    net.add_train_op(name='sa', lossFunc='SA', learning_rate=1e-3, decay_steps=None, decay_rate=None,
                     method='Adam', wd_lambda=0.0)


    # create directories to save the learnt models
    for method in ['sse','csa','sa']:
        model_dir = os.path.join('models','test_ae_mlp_adv_%s'%(method))
        if os.path.exists(model_dir):
            # if directory already exists, delete it
            shutil.rmtree(model_dir)
        os.mkdir(model_dir)

        # train a model for each training op
        dataTrain.reset_batch()
        net.train(dataTrain=dataTrain, dataVal=dataVal, train_op_name=method, n_epochs=100, save_addr=model_dir,
                  visualiseRateTrain=10, visualiseRateVal=10, save_epochs=[50, 100])



