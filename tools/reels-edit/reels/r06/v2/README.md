# r06-takes v2

Feedback on v1: the first two phrases were unclear. Keep only the third, show the failed takes in B&W, then continue with something useful.

All pieces come from IMG_3599:
- takes 1–5 of «Если хотите в этом разобраться…», B&W (BW=[0..4]), counter «Дубль N»;
- the tip (chunks 28, 30, 43): a dental-clinic site in 10 minutes, from 25,000 ₽ (FL.ru);
- take 6, the good one, counter «✓ Получилось», closing card.

Build: `make_seg.py D 3599 …` → hybrid aligned.json (failed takes come from take_subs, the tip from align.py, the last take from take_subs) → custom counter cards → render6 → mute after the last word (volume 33.14–33.20).
