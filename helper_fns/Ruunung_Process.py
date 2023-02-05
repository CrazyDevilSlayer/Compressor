#////////////////////////////////////Variables////////////////////////////////////#
master_process = []
sub_process = []


#////////////////////////////////////Master  Process////////////////////////////////////#

###############------Append_Master_Process------###############
def append_master_process(id):
    if id not in master_process:
        master_process.append(id)
    return

###############------Remove_Master_Process------###############
def remove_master_process(id):
    if id in master_process:
        master_process.remove(id)
        return True
    else:
        return False

###############------Return_Master_Process------###############
def get_master_process():
    return master_process



#////////////////////////////////////Sub Process////////////////////////////////////#

###############------Append_Sub_Process------###############
def append_sub_process(id):
    if id not in sub_process:
        sub_process.append(id)
    return

###############------Remove_Sub_Process------###############
def remove_sub_process(id):
    if id in sub_process:
        sub_process.remove(id)
        return True
    else:
        return False

###############------Return_Sub_Process------###############
def get_sub_process():
    return sub_process