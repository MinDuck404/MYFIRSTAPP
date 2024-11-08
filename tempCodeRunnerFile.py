else:
          d=0
          for i in quest:
            if d%2 == 0:
              if i !='':
                traloi=i.lower()
                cauhoi=line.lower()
                if traloi in cauhoi:
                  if (d+1)%2 !=0:
                    if len(quest[d+1])<6:
                      auto(quest[d+1].lower(),q5)
                    else:
                        auto(quest[d+1].lower(),len(quest[d+1])*q6+0.456)
            d+=1