# -*- coding: UTF-8 -*-
import os
from AFR_face import *
import pickle
import copy
import json
import sys


# import struct


class FaceBase:
    # 字典 faces 的结构
    # faces = {
    #     'ID': {
    #         'Name': 'unknown',
    #         'Age': '0',
    #         'FaceFeature': '',
    #         'Gender': ''
    #     },
    # }

    def __init__(self, type=0, faces={}, size=0):
        self.type = type
        self.faces = faces
        self.size = size

    def __del__(self):
        pass

    # 从文件夹批量注册人脸	ID为文件名 (点 前)
    def initFaceFromDir(self, hFDEngine, hFREngine, path):
        lists = os.listdir(path)

        for img in lists:
            inputImage = loadImageData(path + img)
            faceFeature = getFeatureFromImg(hFDEngine, hFREngine, inputImage)
            if faceFeature == 0.0:
                print(' get feature from img fail!')
                continue
            self.add_face(feature=faceFeature, ID=img.split('.')[0], name=img.split('.')[0])
            print(img)



    def add_face(self, feature, ID, name='Unknown', age='unknown', gender='unknown', update = False):
        '''
            add_face:添加人脸数据
            如果不更新:
                先检查是否有重复的人脸ID
                有重复的ID,返回-1 (表示添加失败)
                如果没有重复的ID,成功插入后返回0
            如果更新特征
                成功插入后返回0 ,添加失败返回-1 (表示添加失败)
        '''

        if update:
            for k, v in self.faces.iteritems():
                if k == ID:
                    print('The ID ={} is exist!'.format(ID))
                    return -1

        self.faces[ID] = {'Name': name, 'FaceFeature': feature, 'Age': age, 'Gender': gender}
        self.size += 1
        # feature.freeUnmanaged()
        return 0

    # 保存
    def savefacedata(self, path='facedata', filename='facedata.pkl', bytetype=False):

        try:
            self.featureToBytes()
            if not os.path.exists(path):
                os.mkdir(path)
            with open(os.path.join(path, filename), 'wb') as f:
                pickle.dump(self.faces, f)
            print('Success save faces feature data ')
        except Exception as e:
            print(e)
        finally:
            if not bytetype:
                self.featureFromBytes()

            # 转化为 byte 格式,以便于保存成文件

    def featureToBytes(self):
        for k, v in self.faces.iteritems():
            # print(v['FaceFeature'])
            # feature_temp = v['FaceFeature'].deepCopy()
            feature_temp = v['FaceFeature']

            self.faces[k]['FaceFeature'] = feature_temp.toByteArray()
            # feature_temp.freeUnmanaged()

        # 将特征从 byte 格式转换成 虹软格式

    def featureFromBytes(self):
        feature_temp = AFR_FSDK_FACEMODEL()
        try:

            for k, v in self.faces.iteritems():
                # feature_temp = AFR_FSDK_FACEMODEL()
                v['FaceFeature'] = feature_temp.fromByteArray(v['FaceFeature'])

        except Exception as e:
            print(e)
        finally:
            feature_temp.freeUnmanaged()

        # 从文件中加载数据

    def loadfacedata(self, path='facedata', filename='facedata.pkl'):

        if not os.path.exists(os.path.join(path, filename)):
            print('file ' + filename + ' not exist! now new an facedata file')
            self.savefacedata(path, filename)

        with open(os.path.join(path, filename), 'rb') as f:
            try:
                # binfaces = f.read()
                # self.faces = struct.unpack('1024p', binfaces)
                self.faces = pickle.load(f)
            except:
                print('file ' + filename + ' not exist! now new an facedata file')
                self.savefacedata(path, filename)
            finally:

                print('success load facedata')
        self.featureFromBytes()

    # 释放掉特征
    def freeAllFeature(self):
        for k, v in self.faces.iteritems():
            v['FaceFeature'].freeUnmanaged()

    def getFaceData(self):
        return self.faces.iteritems()

    # input: ID
    # return value{facefeature,age,gender}
    def getValueFromID(self, ID):
        return self.faces[ID]

    def hasID(self, ID):
        return self.faces.has_key(ID)

    def getValueFromFeature(self, feature):
        for k, v in self.faces.iteritems():
            if v['FaceFeature'] == feature:
                return v

    def getIDFromFeature(self, feature):
        for k, v in self.faces.iteritems():
            if v['FaceFeature'] == feature:
                return k

    def getFeatureFromID(self, ID):

        return self.faces[ID]['FaceFeature']


    def changeFaceData(self, ID=None, value={}):
        if ID == None and value['FaceFeature'] != None:
            ID = self.getIDFromFeature(value['FaceFeature'])

        elif ID == None and value['FaceFeature'] == None:
            print ('fail to change face data')
            return -1


        self.faces[ID] = value

        print('fail to Find ID ={} data'.format(ID))
        return -1

    def removeFaceFeature(self, ID=None, feature=None):
        if ID is None:
            if feature is not None:
                ID = self.getIDFromFeature(feature)
            else:
                return -1
        try:
            if self.faces.has_key(ID):
                print(self.faces.pop(ID)+ 'has remove')

            return 0
        except Exception as e:
            print(e)


# '''
# def initfacefromdir(hFDEngine, hFREngine, path, facebase):
#     lists = os.listdir(path)
#
#     for img in lists:
#         inputImage = loadImageData(path + img)
#         faceInfos, i = doFaceDetection(hFDEngine, inputImage)
#         if len(faceInfos) < 1:
#             print(u'no face in Image ')
#             return 0.0
#
#         # Extract Face Feature 提取人脸特征
#         faceFeature = extractFRFeature(hFREngine, inputImage, faceInfos[i])
#         if faceFeature == None:
#             print(u'extract face feature in Image faile')
#             return 0.0
#
#         if -1 == facebase.add_face(faceFeature,ID=img.split('.')[0],Name=img.split('_')[0] + '_' +img.split('_')[1]):
#             print('Fail to add this face !')
#
#
# # 注册人脸
# def initface(hFDEngine, hFREngine, facebase, inputImage, ID, Name='Unknow'):
#     # 人脸检测
#     faceInfos, i = doFaceDetection(hFDEngine, inputImage)
#     if len(faceInfos) < 1:
#         print(u'no face in Image ')
#         return 0.0
#
#     # Extract Face Feature 提取人脸特征
#     faceFeature = extractFRFeature(hFREngine, inputImage, faceInfos[i])
#     if faceFeature == None:
#         print(u'extract face feature in Image faile')
#         return 0.0
#
#     if -1 == facebase.add_face(feature=faceFeature, ID=ID, Name=Name):
#         print('fail to add this face!')
# '''
#
# def addFaceWithARC(ID, pic_path, name='Unknown', age='Unknown', gender='Unknown):
#     # addFaceFeature(self, ID, pic_path, name='Unknown', age='Unknown', gender='Unknown'):
#     inputImage = loadImageData(pic_path)
#     faceFeature = getFeatureFromImg(self.hFDEngine, self.hFREngine, inputImage)
#     if faceFeature == 0.0:
#         print(' get feature from img fail!')
#         return
#
#     self.facebase.add_face(faceFeature, ID, name, age, gender)

if __name__ == u'__main__':
    # init Engine
    pFDWorkMem = CLibrary.malloc(c_size_t(FD_WORKBUF_SIZE))
    pFRWorkMem = CLibrary.malloc(c_size_t(FR_WORKBUF_SIZE))

    hFDEngine = c_void_p()
    ret = AFD_FSDK_InitialFaceEngine(APPID, FD_SDKKEY, pFDWorkMem, c_int32(FD_WORKBUF_SIZE), byref(hFDEngine),
                                     AFD_FSDK_OPF_0_HIGHER_EXT, 32, MAX_FACE_NUM)
    if ret != 0:
        CLibrary.free(pFDWorkMem)
        print(u'AFD_FSDK_InitialFaceEngine ret 0x{:x}'.format(ret))
        exit(0)

    # print FDEngine version
    versionFD = AFD_FSDK_GetVersion(hFDEngine)
    print(u'{} {} {} {}'.format(versionFD.contents.lCodebase, versionFD.contents.lMajor, versionFD.contents.lMinor,
                                versionFD.contents.lBuild))
    print(c_char_p(versionFD.contents.Version).value.decode(u'utf-8'))
    print(c_char_p(versionFD.contents.BuildDate).value.decode(u'utf-8'))
    print(c_char_p(versionFD.contents.CopyRight).value.decode(u'utf-8'))

    hFREngine = c_void_p()
    ret = AFR_FSDK_InitialEngine(APPID, FR_SDKKEY, pFRWorkMem, c_int32(FR_WORKBUF_SIZE), byref(hFREngine))
    if ret != 0:
        AFD_FSDKLibrary.AFD_FSDK_UninitialFaceEngine(hFDEngine)
        CLibrary.free(pFDWorkMem)
        CLibrary.free(pFRWorkMem)
        print(u'AFR_FSDK_InitialEngine ret 0x{:x}'.format(ret))
        sys.exit(0)

    # print FREngine version
    versionFR = AFR_FSDK_GetVersion(hFREngine)
    print(u'{} {} {} {}'.format(versionFR.contents.lCodebase, versionFR.contents.lMajor, versionFR.contents.lMinor,
                                versionFR.contents.lBuild))
    print(c_char_p(versionFR.contents.Version).value.decode(u'utf-8'))
    print(c_char_p(versionFR.contents.BuildDate).value.decode(u'utf-8'))
    print(c_char_p(versionFR.contents.CopyRight).value.decode(u'utf-8'))

    input_face = 'facedata/faces/'
    # input_face = 'output/'

    face = FaceBase()
    # 加载 input_face 目录下的图片,批量提取特征
    face.initFaceFromDir(hFDEngine, hFREngine, input_face)
    # 将含有特征字典保存到文件
    face.savefacedata()
    face.freeAllFeature()
    print(face.size)
    # face.loadfacedata()

    # release Engine
    AFD_FSDK_UninitialFaceEngine(hFDEngine)
    AFR_FSDK_UninitialEngine(hFREngine)

    CLibrary.free(pFDWorkMem)
    CLibrary.free(pFRWorkMem)
