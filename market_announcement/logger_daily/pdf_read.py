from urllib.request import urlopen

from pdfminer.pdfinterp import PDFResourceManager,process_pdf

from pdfminer.converter import TextConverter

from pdfminer.layout import LAParams

from io import StringIO
import re,logging
from io import open
import traceback
import scrapy

import warnings


warnings.filterwarnings('error')

# def readPDF(pdffile):
#
#     rsrcmgr=PDFResourceManager()
#
#     retstr=StringIO()
#
#     laparams=LAParams()
#
#     device=TextConverter(rsrcmgr,retstr,laparams=laparams)
#
#     process_pdf(rsrcmgr,device,pdffile)
#
#     device.close()
#
#     content=retstr.getvalue()
#
#     retstr.close()
#
#     return content

# try:
#     rsrcmgr = PDFResourceManager()
#     retstr = StringIO()
#     laparams = LAParams()
#     device = TextConverter(rsrcmgr, retstr, laparams=laparams)
#
#     pdffile=urlopen('http://www.cninfo.com.cn/finalpage/2018-07-02/1205112392.PDF')
#     print('---------11',pdffile)
#
#     process_pdf(rsrcmgr, device, pdffile)
#     print('---------22',pdffile)
#
#     device.close()
#     print('---------33',pdffile)
#
#     content = retstr.getvalue()
#     # print(content)
#     retstr.close()
#
#     annc_data = re.sub("\n|\t|\s|\r","",content)
#     print(annc_data)
# except Exception as e:
#     er = traceback.format_exc()
#     print('111',e)


pdffile = urlopen('http://www.cninfo.com.cn/finalpage/2018-07-09/1205136301.PDF')
# pdffile = urlopen('http://www.cninfo.com.cn/finalpage/2018-07-02/1205112399.PDF')
print(pdffile,'----3',type(pdffile))
# logging.propagate = False
# logging.getLogger().setLevel(logging.ERROR)

def readpdf(filepdf):
    try:
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()

        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        print('1111---')

        process_pdf(rsrcmgr, device, filepdf)
        device.close()
        content = retstr.getvalue()
        retstr.close()
    except Exception as e:
        content = ' '
        err = traceback.format_exc()
        print('1212--',e,'1212--')
    return content

annc_title = readpdf(pdffile)
annc_title = re.sub("\n|\t|\\s|\r", "", annc_title)

print('qqq---',annc_title)


# # pdffile=urlopen('http://www.cninfo.com.cn/finalpage/2018-07-16/1205156711.PDF')
#
# # outputString=readPDF(pdffile)
#
# # print(outputString)
#
# pdffile.close()



#
# import logging
# from urllib.request import urlopen
#
# logging.Logger.propagate = False
# logging.getLogger().setLevel(logging.ERROR)
#
# from pdfminer.converter import PDFPageAggregator
# from pdfminer.layout import LAParams
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.pdfparser import PDFParser, PDFDocument
#
# # fp = open('template/pdftest.pdf', 'rb')
# # 在线
# fp = urlopen('http://www.cninfo.com.cn/finalpage/2018-07-16/1205161743.PDF')
#
# # 创建一个与文档关联的解析器
# parser = PDFParser(fp)
#
# # PDF文档对象
# doc = PDFDocument()
#
# # 链接解析器和文档对象
# parser.set_document(doc)
# doc.set_parser(parser)
#
# # 初始化文档
# doc.initialize("")
#
# # 创建DPF资源管理器
# resource = PDFResourceManager()
#
# # 参数分析器
# laparam = LAParams()
#
# # 聚合器
# device = PDFPageAggregator(resource, laparams=laparam)
#
# # 创建页面解析器
# interpreter = PDFPageInterpreter(resource, device)
#
# # 使用文档对象从pdf中读取内容
# for page in doc.get_pages():
#     # 使用页面解析器
#     interpreter.process_page(page)
#
#     layout = device.get_result()
#     # 使用聚合器获取内容
#     for out in layout:
#         # 判断是否有get_text属性
#         if hasattr(out, 'get_text'):
#             print(out.get_text())
#
# if __name__ == '__main__':
#     pass



#
#
# from PyPDF2 import PdfFileReader, PdfFileWriter
# infn = '1205156699.PDF'
# outfn = '123.txt'
# # # 获取一个 PdfFileReader 对象
# # pdf_input = PdfFileReader(open(infn, 'rb'))
# # # 获取 PDF 的页数
# # page_count = pdf_input.getNumPages()
# # print(page_count)
# # # 返回一个 PageObject
# # page = pdf_input.getPage(22)
# #
# # # 获取一个 PdfFileWriter 对象
# # pdf_output = PdfFileWriter()
# # # 将一个 PageObject 加入到 PdfFileWriter 中
# # pdf_output.addPage(page)
# # # 输出到文件中
# # pdf_output.write(open(outfn, 'wb'))
#
# pdf = PdfFileReader(open(infn, "rb"))
# content = ""
# for i in range(0, pdf.getNumPages()):
#     pageObj = pdf.getPage(i)
#
#     extractedText = pageObj.extractText()
#     content += extractedText + "\n"
# print(content)