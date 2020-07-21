'''
utt_code_maya.py 
date: 2020.06.23
ver: 1.1

format:
  * #x3 = section
  * #~2 = sub tree

log:
  * example here

'''
### Rig code

#~~ rig start
cmds.file(new=1, f=1)

### camera operation
#~~ get current look at camera
# get current look at camera
cmds.lookThru(q=1)
#~~ get image plane file pixel size
pixmapSize = cmds.imagePlane(cur_imagePlane, q=1,iz=1)

###preference
#~~ hide inview help
cmds.optionVar(iv=('inViewMessageEnable',0))

###END