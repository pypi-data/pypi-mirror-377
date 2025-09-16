from beans.BeansTable import BeansTable

def testReadFromBeans():
    token = "cfa7b89f7ed170637ca5cd5bc2d490a2"
    
    dsQuery = ""
    tbQuery = "1bb4a264653fe29aafd8183c5ac8d1af"
    
    outDs = "c283bbd82c231082bce3c36c9c39ff7a"
    outTb = "out name 1"
    
    out = BeansTable(token, outDs, outTb)
    inp = BeansTable(token, dsQuery, tbQuery)
    out.write("# time ns\n")
    for l in inp:
        if l['m'] > 80.0:
            # print(l)
            out.write(str(l['time']) + " " + str(l['ns']) + "\n")
    out.close()

if __name__ == '__main__':
    testReadFromBeans()
    print("Finished!")