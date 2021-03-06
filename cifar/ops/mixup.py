
import torch



class MixUper(object):
    def __init__(self, alpha, lb_encoder, mixup='none'):
        self.mixup = mixup
        self.beta_generator = torch.distributions.beta.Beta(alpha, alpha)
        self.lb_encoder = lb_encoder

    def __call__(self, ims, lbs):
        assert ims.size(0) == lbs.size(0)
        lbs = self.lb_encoder(lbs)

        if self.mixup == 'none':
            pass
        elif self.mixup == 'mixup':
            bs = ims.size(0)
            lam = self.beta_generator.sample([bs, 1, 1, 1]).cuda()
            lam = torch.where(lam > (1. - lam), lam, (1. - lam))
            indices = torch.randperm(bs)
            ims = lam * ims + (1. - lam) * ims[indices]
            lam = lam.view(-1, 1)
            lbs = lam * lbs + (1. - lam) * lbs[indices]

        return ims, lbs
