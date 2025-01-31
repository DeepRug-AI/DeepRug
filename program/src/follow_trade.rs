use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

#[program]
pub mod follow_trade {
    use super::*;

    pub fn initialize(
        ctx: Context<Initialize>,
        follow_fee: u64,
        burn_rate: u8,
    ) -> Result<()> {
        let state = &mut ctx.accounts.state;
        state.owner = ctx.accounts.owner.key();
        state.follow_fee = follow_fee;
        state.burn_rate = burn_rate;
        state.total_followers = 0;
        Ok(())
    }

    pub fn start_follow(
        ctx: Context<StartFollow>,
        symbol: String,
    ) -> Result<()> {
        let follow = &mut ctx.accounts.follow;
        follow.trader = ctx.accounts.trader.key();
        follow.follower = ctx.accounts.follower.key();
        follow.symbol = symbol;
        follow.active = true;
        follow.timestamp = Clock::get()?.unix_timestamp;

        let state = &mut ctx.accounts.state;
        state.total_followers = state.total_followers.checked_add(1).unwrap();

        emit!(FollowStarted {
            trader: follow.trader,
            follower: follow.follower,
            symbol: follow.symbol.clone(),
            timestamp: follow.timestamp,
        });

        Ok(())
    }

    pub fn distribute_profit(
        ctx: Context<DistributeProfit>,
        amount: u64,
    ) -> Result<()> {
        let follow = &ctx.accounts.follow;
        require!(follow.active, ErrorCode::FollowNotActive);

        // Calculate profit share
        let trader_share = (amount * 70) / 100; // 70% to trader
        let follower_share = amount - trader_share; // 30% to follower

        // Transfer profit shares
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.profit_pool.to_account_info(),
                    to: ctx.accounts.trader_token.to_account_info(),
                    authority: ctx.accounts.state.to_account_info(),
                },
            ),
            trader_share,
        )?;

        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.profit_pool.to_account_info(),
                    to: ctx.accounts.follower_token.to_account_info(),
                    authority: ctx.accounts.state.to_account_info(),
                },
            ),
            follower_share,
        )?;

        emit!(ProfitDistributed {
            trader: follow.trader,
            follower: follow.follower,
            amount,
            trader_share,
            follower_share,
        });

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = owner, space = 8 + State::LEN)]
    pub state: Account<'info, State>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct StartFollow<'info> {
    #[account(init, payer = follower, space = 8 + Follow::LEN)]
    pub follow: Account<'info, Follow>,
    #[account(mut)]
    pub state: Account<'info, State>,
    pub trader: AccountInfo<'info>,
    #[account(mut)]
    pub follower: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct DistributeProfit<'info> {
    #[account(mut)]
    pub follow: Account<'info, Follow>,
    #[account(mut)]
    pub state: Account<'info, State>,
    #[account(mut)]
    pub profit_pool: Account<'info, TokenAccount>,
    #[account(mut)]
    pub trader_token: Account<'info, TokenAccount>,
    #[account(mut)]
    pub follower_token: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

#[account]
pub struct State {
    pub owner: Pubkey,
    pub follow_fee: u64,
    pub burn_rate: u8,
    pub total_followers: u64,
}

#[account]
pub struct Follow {
    pub trader: Pubkey,
    pub follower: Pubkey,
    pub symbol: String,
    pub active: bool,
    pub timestamp: i64,
}

#[event]
pub struct FollowStarted {
    pub trader: Pubkey,
    pub follower: Pubkey,
    pub symbol: String,
    pub timestamp: i64,
}

#[event]
pub struct ProfitDistributed {
    pub trader: Pubkey,
    pub follower: Pubkey,
    pub amount: u64,
    pub trader_share: u64,
    pub follower_share: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Follow is not active")]
    FollowNotActive,
}