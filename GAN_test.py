#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from functools import partial
import numpy
from matplotlib import pyplot
# Define a PDF
#PDF的解释：https://zh.wikipedia.org/wiki/%E6%A9%9F%E7%8E%87%E5%AF%86%E5%BA%A6%E5%87%BD%E6%95%B8（需科学上网)
x_samples = numpy.arange(-3,3.01,0.01)
PDF=numpy.empty(x_samples.shape)
PDF[x_samples < 0] = numpy.round(x_samples[x_samples < 0] + 3.5) /3
PDF[x_samples >=0] = 0.5 * numpy.cos(numpy.pi * x_samples[x_samples >=0]) + 0.5
PDF /= numpy.sum(PDF)
#Calculate approximated CDF
#CDF的解释：https://zh.wikipedia.org/zh-cn/%E7%B4%AF%E7%A7%AF%E5%88%86%E5%B8%83%E5%87%BD%E6%95%B0 (需科学上网)
CDF=numpy.empty(PDF.shape)
cumulated=0
for i in range(CDF.shape[0]):
    cumulated += PDF[i]
    CDF[i]=cumulated
# Generate samples
generate=partial(numpy.interp,xp=CDF,fp=x_samples)
u_rv=numpy.random.random(10000)
x=generate(u_rv)
# Visualization
fig,(ax0,ax1)=pyplot.subplots(ncols=2,figsize=(9,4))
ax0.plot(x_samples,PDF)
ax0.axis([-3.5,3.5,0,numpy.max(PDF)*1.1])
ax1.hist(x,100)
pyplot.show()
#原文网址：https://zhuanlan.zhihu.com/p/27199954