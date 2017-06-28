from __future__ import print_function
import json, os, traceback
from binaryninja import LowLevelILOperation, LowLevelILInstruction

expr_attrs = ['src', 'dest', 'hi', 'lo', 'left', 'right', 'condition']

with open(os.path.expanduser("~") + '/.binaryninja/plugins/binja_explain_instruction/' + 'explanations_en.json', 'r') as explanation_file:
    explanations = json.load(explanation_file)

def preprocess_LLIL_CALL(bv, llil_instruction):
    func = bv.get_function_at(llil_instruction.dest.constant)
    if func is not None:
        llil_instruction.dest = func.name
    return llil_instruction

def preprocess_LLIL_CONST(_bv, llil_instruction):
    llil_instruction.constant = llil_instruction.tokens[0]# hex(llil_instruction.constant).replace('L','')
    return llil_instruction

def preprocess_jump(_bv, llil_instruction):
    llil_instruction.dest = llil_instruction.tokens[-1]
    return llil_instruction

preprocess_dict = {
    "LLIL_CALL": preprocess_LLIL_CALL,
    "LLIL_IF": preprocess_jump,
    "LLIL_GOTO": preprocess_jump,
    "LLIL_CONST": preprocess_LLIL_CONST
}

def preprocess(bv, llil_instruction):
    if llil_instruction.operation.name in preprocess_dict:
        out = preprocess_dict[llil_instruction.operation.name](bv, llil_instruction)
        llil_instruction = out if out is not None else llil_instruction
    for attr in expr_attrs:
        if hasattr(llil_instruction, attr):
            unexplained = llil_instruction.__getattribute__(attr)
            if type(unexplained) == LowLevelILInstruction:
                llil_instruction.__setattr__(attr, explain_llil(bv, unexplained))
    return llil_instruction

def explain_llil(bv, llil_instruction):
    if llil_instruction is None:
        return
    if llil_instruction.operation.name in explanations:
        try:
            return explanations[llil_instruction.operation.name].format(llil=preprocess(bv, llil_instruction))
        except AttributeError:
            print("Bad Format String")
            traceback.print_exc()
            return llil_instruction.operation.name
    print("We don't understand", llil_instruction.operation.name, "yet")
    return llil_instruction.operation.name
