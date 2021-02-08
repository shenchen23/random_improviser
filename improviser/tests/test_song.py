from improviser.song import *

print(Mode("C","Phrygian"))
print(Chord(root='C',other_notes=[Note("E"),Note("G"),Note("B")]))

test_df = pd.DataFrame({"bar":[1]*4,"key":['C']*4,"mode":['Ionian']*4,"degree":[4,3,2,1]})
test_df['chord_name'] = test_df.apply(lambda x: (FunctionalChord(key = x.key,mode_name = x['mode'],degree = x.degree).chord.name), axis = 1)

print(test_df)